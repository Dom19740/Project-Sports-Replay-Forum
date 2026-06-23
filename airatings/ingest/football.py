import os
import logging
import datetime
import requests
from django.conf import settings
from django.core.cache import cache
from .base import EventDataSource
from .reports import fetch_matching_reports

logger = logging.getLogger(__name__)

_TIMEOUT = 12
_CACHE_TTL = 60 * 60 * 24  # 24 h — finished events don't change

# Stats keys as returned by TheSportsDB lookupeventstats
_STAT_SHOTS_ON_GOAL = "Shots on Goal"
_STAT_TOTAL_SHOTS   = "Total Shots"
_STAT_POSSESSION    = "Ball Possession"
_STAT_XG            = "expected_goals"


# ---------------------------------------------------------------------------
# Shared HTTP + cache helper
# ---------------------------------------------------------------------------

def _sportsdb_fetch(endpoint: str, id_event: str) -> dict | None:
    cache_key = f"sportsdb_{endpoint}_{id_event}"
    hit = cache.get(cache_key)
    if hit is not None:
        return hit

    api_key = os.environ.get("SPORTSDB_API_KEY")
    if not api_key:
        logger.warning("SPORTSDB_API_KEY not set; skipping %s", endpoint)
        return None

    url = f"https://www.thesportsdb.com/api/v1/json/{api_key}/{endpoint}?id={id_event}"
    try:
        r = requests.get(url, timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        cache.set(cache_key, data, _CACHE_TTL)
        return data
    except Exception as exc:
        logger.warning("TheSportsDB %s/%s failed: %s", endpoint, id_event, exc)
        return None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _int(val) -> int:
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _float(val) -> float | None:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _parse_stats(eventstats: list) -> dict:
    """Flatten the eventstats list into {strStat: (intHome, intAway)}."""
    result = {}
    for entry in (eventstats or []):
        key = entry.get("strStat", "")
        result[key] = (entry.get("intHome"), entry.get("intAway"))
    return result


def _goal_events(timeline: list) -> list:
    return [e for e in (timeline or []) if e.get("strTimeline", "").lower() == "goal"]


def _card_events(timeline: list) -> list:
    return [e for e in (timeline or []) if e.get("strTimeline", "").lower() == "card"]


def _detect_comeback(goal_events: list, final_home: int, final_away: int) -> bool:
    """
    True if the eventual winner (or either team for a draw) was behind at any
    point during the match, inferred from goal-by-goal progression.
    """
    if not goal_events:
        return False

    home_score = away_score = 0
    home_was_behind = away_was_behind = False

    for g in sorted(goal_events, key=lambda g: _int(g.get("intTime", 0))):
        if g.get("strHome", "").lower() == "yes":
            home_score += 1
        else:
            away_score += 1

        if home_score < away_score:
            home_was_behind = True
        if away_score < home_score:
            away_was_behind = True

    if final_home > final_away:
        return home_was_behind
    if final_away > final_home:
        return away_was_behind
    # draw — comeback if either team recovered from being behind
    return home_was_behind or away_was_behind


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------

class FootballDataSource(EventDataSource):

    def get_stats(self, event) -> dict:
        id_event = event.idEvent
        stats: dict = {"has_detailed_events": False}

        # --- lookupevent --------------------------------------------------
        event_data = _sportsdb_fetch("lookupevent.php", id_event)
        raw_event = (event_data or {}).get("events", [None])[0]
        if not raw_event:
            logger.warning("FootballDataSource: no lookupevent data for %s", id_event)
            return stats

        home_team = raw_event.get("strHomeTeam", "")
        away_team = raw_event.get("strAwayTeam", "")
        home_goals = _int(raw_event.get("intHomeScore"))
        away_goals = _int(raw_event.get("intAwayScore"))

        stats.update({
            "sport": "football",
            "competition": event.event_list.league,
            "home_team": home_team,
            "away_team": away_team,
            "home_goals": home_goals,
            "away_goals": away_goals,
            "total_goals": home_goals + away_goals,
            "margin": abs(home_goals - away_goals),
            "venue": raw_event.get("strVenue", ""),
            "group": raw_event.get("strGroup", ""),
        })

        # --- lookupeventstats --------------------------------------------
        stats_data = _sportsdb_fetch("lookupeventstats.php", id_event)
        parsed = _parse_stats((stats_data or {}).get("eventstats", []))

        def stat(key, cast=_int, side="home"):
            h, a = parsed.get(key, (None, None))
            val = h if side == "home" else a
            return cast(val) if val is not None else None

        stats.update({
            "shots_on_goal_home":  stat(_STAT_SHOTS_ON_GOAL, _int, "home"),
            "shots_on_goal_away":  stat(_STAT_SHOTS_ON_GOAL, _int, "away"),
            "total_shots_home":    stat(_STAT_TOTAL_SHOTS,   _int, "home"),
            "total_shots_away":    stat(_STAT_TOTAL_SHOTS,   _int, "away"),
            "possession_home":     stat(_STAT_POSSESSION,    _int, "home"),
            "xg_home":             stat(_STAT_XG,            _float, "home"),
            "xg_away":             stat(_STAT_XG,            _float, "away"),
        })

        # --- lookuptimeline ----------------------------------------------
        timeline_data = _sportsdb_fetch("lookuptimeline.php", id_event)
        timeline = (timeline_data or {}).get("timeline", []) or []

        goals  = _goal_events(timeline)
        cards  = _card_events(timeline)

        has_detail = bool(timeline)
        stats["has_detailed_events"] = has_detail

        goal_minutes = sorted(_int(g.get("intTime", 0)) for g in goals if g.get("intTime"))
        stats["goal_minutes"] = goal_minutes
        stats["has_late_goal"]      = any(m >= 80 for m in goal_minutes)
        stats["has_very_late_goal"] = any(m >= 90 for m in goal_minutes)

        stats["comeback"] = _detect_comeback(goals, home_goals, away_goals) if has_detail else False

        red_cards    = sum(1 for c in cards if "red" in c.get("strTimelineDetail", "").lower())
        yellow_cards = sum(1 for c in cards if "yellow" in c.get("strTimelineDetail", "").lower())

        # Fall back to eventstats card counts if timeline is thin
        if not has_detail:
            red_cards    = stat("Red Cards",    _int, "home") or 0
            red_cards   += stat("Red Cards",    _int, "away") or 0
            yellow_cards = stat("Yellow Cards", _int, "home") or 0
            yellow_cards += stat("Yellow Cards", _int, "away") or 0

        stats["red_cards"]    = red_cards
        stats["yellow_cards"] = yellow_cards

        penalty_from_timeline = any(
            "penalty" in (g.get("strTimelineDetail") or "").lower() for g in goals
        )
        penalty_from_stats = (parsed.get("Penalty Goals") is not None)
        stats["penalties"] = penalty_from_timeline or penalty_from_stats

        # --- lookuplineup ------------------------------------------------
        lineup_data = _sportsdb_fetch("lookuplineup.php", id_event)
        lineup = (lineup_data or {}).get("lineup", []) or []
        # Count starters per side (strSubstitute == "No") — used for high-profile context
        stats["home_starters"] = sum(
            1 for p in lineup
            if p.get("strHome") == "Yes" and p.get("strSubstitute", "").lower() == "no"
        )
        stats["away_starters"] = sum(
            1 for p in lineup
            if p.get("strHome") == "No" and p.get("strSubstitute", "").lower() == "no"
        )

        return stats

    def get_reports(self, event) -> list[str]:
        event_data = _sportsdb_fetch("lookupevent.php", event.idEvent)
        raw = (event_data or {}).get("events", [None])[0] or {}
        home_team = raw.get("strHomeTeam", "")
        away_team = raw.get("strAwayTeam", "")
        if not home_team or not away_team:
            return []

        day = event.date_time.replace(tzinfo=datetime.timezone.utc)
        since = day - datetime.timedelta(days=1)
        until = day + datetime.timedelta(days=1)

        feeds = getattr(settings, "FOOTBALL_RSS_FEEDS", [])
        return fetch_matching_reports(
            feed_urls=feeds,
            keywords=[home_team, away_team],
            since=since,
            until=until,
        )
