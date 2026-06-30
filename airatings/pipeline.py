import logging

from airatings.guard import run_with_guard
from airatings.ingest.dispatch import get_source_for_event
from airatings.models import AIRating, EventSignals
from airatings.stage_one import extract_signals
from airatings.verdict import (
    HOT_WATCH_MIN_STARS,
    MID_TEMP_MIN_STARS,
    VERDICT_HOT,
    VERDICT_MID,
    VERDICT_NOT,
    map_to_verdict,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Finished-status detection
# ---------------------------------------------------------------------------

_FOOTBALL_FINISHED_STATUSES = {"FT", "AET", "PEN", "AP", "AOT", "FT_PEN", "Finished"}
_FOOTBALL_LEAGUES = {"FIFA World Cup", "English Premier League"}
_F1_LEAGUES = {"Formula 1"}


def is_event_finished(event) -> bool:
    """
    Ask the live API whether the event has concluded.
    Uses cached responses where available — no redundant HTTP calls.
    """
    league = event.event_list.league

    if league in _FOOTBALL_LEAGUES:
        try:
            from airatings.ingest.football import _sportsdb_fetch
            data = _sportsdb_fetch("lookupevent.php", event.idEvent)
            events = (data or {}).get("events") or []
            if not events:
                return False
            status = events[0].get("strStatus", "")
            finished = status in _FOOTBALL_FINISHED_STATUSES
            if not finished:
                logger.debug(
                    "pipeline: event pk=%s status=%r — not finished yet",
                    event.pk, status,
                )
            return finished
        except Exception as exc:
            logger.warning("pipeline: status check failed for event pk=%s: %s", event.pk, exc)
            # If the API is rate-limiting us, fall back to time-based check:
            # if kickoff was 4+ hours ago the match is almost certainly over.
            from django.utils import timezone as _tz
            hours_since = (_tz.now() - event.date_time).total_seconds() / 3600
            if hours_since >= 4:
                logger.info(
                    "pipeline: assuming finished for event pk=%s (%.1fh since kickoff, API unavailable)",
                    event.pk, hours_since,
                )
                return True
            return False

    if league in _F1_LEAGUES:
        try:
            from airatings.ingest.f1 import F1DataSource, _jolpica_get
            year = event.date_time.year
            round_num = F1DataSource()._find_round(year, event.event_list.name)
            if not round_num:
                return False
            data = _jolpica_get(f"/{year}/{round_num}/results.json")
            races = (data or {}).get("MRData", {}).get("RaceTable", {}).get("Races", [])
            return bool(races and races[0].get("Results"))
        except Exception as exc:
            logger.warning("pipeline: F1 status check failed for event pk=%s: %s", event.pk, exc)
            return False

    # Unknown league — fall back to the event's own flag
    return bool(getattr(event, "is_finished", False))


# ---------------------------------------------------------------------------
# Stat-based signal corrections (deterministic safety net)
# ---------------------------------------------------------------------------

# Goal-count floors for football: a high-scoring game is inherently entertaining
# regardless of how competitive it was. The LLM can underestimate excitement
# for dominant goal-fests — these floors prevent that.
_GOAL_EXCITEMENT_FLOORS = (
    (7, 5),  # 7+ goals → excitement must be at least 5
    (5, 4),  # 5-6 goals → excitement must be at least 4
    (4, 3),  # 4 goals → excitement must be at least 3
)


def _stars_to_verdict(stars: int) -> str:
    if stars >= HOT_WATCH_MIN_STARS:
        return VERDICT_HOT
    if stars >= MID_TEMP_MIN_STARS:
        return VERDICT_MID
    return VERDICT_NOT


def _apply_stat_corrections(signals: dict, stats: dict) -> dict:
    """
    Apply deterministic corrections to LLM-generated signals based on hard stats.

    This is a one-way floor, not a ceiling — it can only raise excitement for
    high-scoring matches. It never lowers signals; the improved Stage One prompt
    handles over-inflation.

    Currently handles football only (total_goals field).
    """
    sport = stats.get("sport", "")
    if sport != "football":
        return signals

    total_goals = int(stats.get("total_goals") or 0)
    current_excitement = signals.get("excitement", 1)

    for goal_threshold, excitement_floor in _GOAL_EXCITEMENT_FLOORS:
        if total_goals >= goal_threshold and current_excitement < excitement_floor:
            corrected = dict(signals)
            corrected["excitement"] = excitement_floor
            logger.info(
                "stat_correction: excitement raised %d→%d (total_goals=%d ≥ %d)",
                current_excitement, excitement_floor, total_goals, goal_threshold,
            )
            return corrected

    return signals


# Goal-count floors at the verdict level: a high-scoring game deserves a
# minimum star rating regardless of how one-sided it was. A 7-1 thrashing
# is entertaining as a goal-fest even if drama/competitiveness are low.
_GOAL_STAR_FLOORS = (
    (7, 4),  # 7+ goals → at least 4★ (HOT WATCH)
    (5, 3),  # 5-6 goals → at least 3★ (MID TEMP)
    (4, 2),  # 4 goals → at least 2★ — a 4-goal game is never NOT WATCH
)


def _apply_verdict_corrections(verdict: dict, stats: dict) -> dict:
    """
    Apply deterministic star-level floors based on goal count.

    Parallel to _apply_stat_corrections but operates on the verdict dict
    after map_to_verdict(). One-way floor only — never lowers stars.
    Football only.
    """
    sport = stats.get("sport", "")
    if sport != "football":
        return verdict

    total_goals = int(stats.get("total_goals") or 0)
    current_stars = verdict["stars"]

    for goal_threshold, star_floor in _GOAL_STAR_FLOORS:
        if total_goals >= goal_threshold and current_stars < star_floor:
            new_verdict = _stars_to_verdict(star_floor)
            corrected = dict(verdict)
            corrected["stars"] = star_floor
            corrected["verdict"] = new_verdict
            corrected["rationale_internal"] = (
                verdict["rationale_internal"]
                + f" | verdict_correction: stars raised {current_stars}★→{star_floor}★"
                f" (total_goals={total_goals} ≥ {goal_threshold})"
            )
            logger.info(
                "verdict_correction: stars raised %d★→%d★ %s→%s (total_goals=%d ≥ %d)",
                current_stars, star_floor,
                verdict["verdict"], new_verdict,
                total_goals, goal_threshold,
            )
            return corrected

    return verdict


# ---------------------------------------------------------------------------
# Pipeline error
# ---------------------------------------------------------------------------

class PipelineError(Exception):
    pass


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(event, force: bool = False) -> AIRating:
    """
    Run the full AI rating pipeline for one event.

    Stages:
        1. Ingest stats + reports
        2. Stage one — spoiler-full signal extraction (LLM)
        3. Verdict map — deterministic
        4. Stage two + guard — spoiler-free blurb (LLM) with safety check

    Saves result as an AIRating row.

    Idempotency:
        - Already-published ratings are skipped unless force=True.
        - force=True re-runs the full pipeline regardless of existing status.

    Returns the AIRating instance.
    Raises PipelineError if any non-recoverable stage fails.
    """
    # --- Idempotency guard -----------------------------------------------
    if not force:
        try:
            existing = AIRating.objects.get(event=event)
            if existing.status == AIRating.STATUS_PUBLISHED:
                logger.info(
                    "pipeline: event pk=%s already published — skipping", event.pk
                )
                return existing
        except AIRating.DoesNotExist:
            pass

    logger.info("pipeline: starting for event pk=%s (%s)", event.pk, event)

    # --- 1. Ingest --------------------------------------------------------
    source = get_source_for_event(event)
    if source is None:
        raise PipelineError(f"No data source for league '{event.event_list.league}'")

    stats = source.get_stats(event)
    if not stats or stats == {"has_detailed_events": False}:
        raise PipelineError(
            f"get_stats() returned empty for event pk={event.pk} — "
            "event may not be finished yet or API returned no data"
        )

    reports = source.get_reports(event)
    logger.info("pipeline: %d report(s) fetched for event pk=%s", len(reports), event.pk)

    # --- 2. Stage one (LLM) -----------------------------------------------
    try:
        signals = extract_signals(stats, reports)
    except RuntimeError as exc:
        raise PipelineError(f"Stage one failed: {exc}") from exc

    # --- 2b. Stat corrections (deterministic safety net) ------------------
    signals = _apply_stat_corrections(signals, stats)

    EventSignals.objects.update_or_create(
        event=event,
        defaults={"signals": signals},
    )

    # --- 3. Verdict (deterministic) ---------------------------------------
    verdict = map_to_verdict(signals)
    verdict = _apply_verdict_corrections(verdict, stats)

    # --- 4. Stage two + guard (LLM) ----------------------------------------
    blurb, is_safe, flag_reasons = run_with_guard(signals, verdict, event)

    status = AIRating.STATUS_FLAGGED if not is_safe else AIRating.STATUS_PUBLISHED

    # --- 5. Persist -------------------------------------------------------
    ai_rating, created = AIRating.objects.update_or_create(
        event=event,
        defaults={
            "status":             status,
            "stars":              verdict["stars"],
            "verdict":            verdict["verdict"],
            "blurb":              blurb,
            "rationale_internal": verdict["rationale_internal"],
            "flag_reasons":       flag_reasons,
        },
    )

    verb = "Created" if created else "Updated"
    flag_note = f" — FLAGGED: {flag_reasons}" if not is_safe else ""
    logger.info(
        "pipeline: %s AIRating pk=%s for event pk=%s → %d★ %s [%s]%s",
        verb, ai_rating.pk, event.pk,
        verdict["stars"], verdict["verdict"], status, flag_note,
    )

    # Mark event finished so run_ratings skips the API status check next time
    if not event.is_finished:
        event.is_finished = True
        event.save(update_fields=["is_finished"])

    return ai_rating
