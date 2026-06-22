import logging

from airatings.guard import run_with_guard
from airatings.ingest.dispatch import get_source_for_event
from airatings.models import AIRating, EventSignals
from airatings.stage_one import extract_signals
from airatings.verdict import map_to_verdict

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Finished-status detection
# ---------------------------------------------------------------------------

_FOOTBALL_FINISHED_STATUSES = {"FT", "AET", "PEN", "AOT", "FT_PEN", "Finished"}
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
# Pipeline error
# ---------------------------------------------------------------------------

class PipelineError(Exception):
    pass


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(event) -> AIRating:
    """
    Run the full AI rating pipeline for one event.

    Stages:
        1. Ingest stats + reports
        2. Stage one — spoiler-full signal extraction (LLM)
        3. Verdict map — deterministic
        4. Stage two + guard — spoiler-free blurb (LLM) with safety check

    Saves result as an AIRating row.

    Idempotency:
        - Already-published ratings are never overwritten.
        - Pending / flagged ratings are re-processed (allows retries after fixes).

    Returns the AIRating instance.
    Raises PipelineError if any non-recoverable stage fails.
    """
    # --- Idempotency guard -----------------------------------------------
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

    EventSignals.objects.update_or_create(
        event=event,
        defaults={"signals": signals},
    )

    # --- 3. Verdict (deterministic) ---------------------------------------
    verdict = map_to_verdict(signals)

    # --- 4. Stage two + guard (LLM) ----------------------------------------
    blurb, is_safe, flag_reasons = run_with_guard(signals, verdict, event)

    status = AIRating.STATUS_FLAGGED if not is_safe else AIRating.STATUS_PENDING

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
