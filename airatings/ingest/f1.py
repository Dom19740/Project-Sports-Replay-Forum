import re
import logging
import datetime
import requests
from django.conf import settings
from django.core.cache import cache
from .base import EventDataSource
from .reports import fetch_matching_reports

logger = logging.getLogger(__name__)

_BASE = "https://api.jolpi.ca/ergast/f1"
_TIMEOUT = 12
_CACHE_TTL = 60 * 60 * 24  # 24 h — race results don't change


# ---------------------------------------------------------------------------
# HTTP + cache helper
# ---------------------------------------------------------------------------

def _jolpica_get(path: str) -> dict | None:
    cache_key = f"jolpica_{path}"
    hit = cache.get(cache_key)
    if hit is not None:
        return hit

    url = f"{_BASE}{path}"
    try:
        r = requests.get(url, timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
        cache.set(cache_key, data, _CACHE_TTL)
        return data
    except Exception as exc:
        logger.warning("Jolpica request failed [%s]: %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _quali_time_to_secs(t: str) -> float | None:
    if not t:
        return None
    try:
        if ":" in t:
            mins, rest = t.split(":", 1)
            return int(mins) * 60 + float(rest)
        return float(t)
    except ValueError:
        return None


def _is_dnf(status: str) -> bool:
    if not status or status == "Finished":
        return False
    return not bool(re.match(r"^\+\d+ Laps?$", status))


# ---------------------------------------------------------------------------
# Name matching helpers
# ---------------------------------------------------------------------------

# Words stripped before comparing location tokens
_GENERIC = {"grand", "prix", "circuit", "de", "the", "race", "gp", "international", "park"}


def _location_tokens(name: str) -> set[str]:
    """Extract meaningful location words from a race/circuit name."""
    tokens = re.split(r"[\s\-\/]+", name.lower())
    return {t for t in tokens if t and t not in _GENERIC and len(t) > 2}


# ---------------------------------------------------------------------------
# Adapter
# ---------------------------------------------------------------------------

class F1DataSource(EventDataSource):

    def _find_round(self, year: int, competition_name: str) -> int | None:
        data = _jolpica_get(f"/{year}.json?limit=30")
        if not data:
            return None
        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        comp_lower = competition_name.lower()
        comp_tokens = _location_tokens(competition_name)

        for race in races:
            ergast_name  = race.get("raceName", "").lower()
            circuit_name = race.get("Circuit", {}).get("circuitName", "").lower()

            # 1. Direct substring match (handles identical or contained names)
            if ergast_name in comp_lower or comp_lower in ergast_name:
                return int(race["round"])

            # 2. Location-token overlap across race name + circuit name.
            #    e.g. "Barcelona-Catalunya GP" vs "Barcelona GP" / "Circuit de Barcelona-Catalunya"
            ergast_tokens = _location_tokens(ergast_name) | _location_tokens(circuit_name)
            if comp_tokens & ergast_tokens:
                return int(race["round"])

        logger.warning("F1: no Ergast round matched '%s' %s", competition_name, year)
        return None

    def _championship_gap(self, year: int, round_num: int) -> float | None:
        """Points gap between P1 and P2 in driver standings BEFORE this round."""
        if round_num <= 1:
            return None
        data = _jolpica_get(f"/{year}/{round_num - 1}/driverStandings.json")
        if not data:
            return None
        lists = data.get("MRData", {}).get("StandingsTable", {}).get("StandingsLists", [])
        if not lists:
            return None
        standings = lists[0].get("DriverStandings", [])
        if len(standings) < 2:
            return None
        try:
            p1 = float(standings[0]["points"])
            p2 = float(standings[1]["points"])
            return round(p1 - p2, 1)
        except (KeyError, ValueError):
            return None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_stats(self, event) -> dict:
        year = event.date_time.year
        round_num = self._find_round(year, event.event_list.name)
        if round_num is None:
            return {"has_detailed_events": False}

        stats: dict = {
            "sport": "f1",
            "event_type": event.event_type,
            "race_name": event.event_list.name,
            "year": year,
            "round": round_num,
            "has_detailed_events": True,
            "championship_gap_before": self._championship_gap(year, round_num),
        }

        if event.event_type == "Race":
            self._add_race_stats(stats, year, round_num)
        elif event.event_type in ("Qualifying", "Sprint Shootout"):
            self._add_qualifying_stats(stats, year, round_num)
        elif event.event_type in ("Sprint", "Sprint Race"):
            self._add_sprint_stats(stats, year, round_num)
        else:
            stats["has_detailed_events"] = False

        return stats

    # ------------------------------------------------------------------
    # Stat builders
    # ------------------------------------------------------------------

    def _add_race_stats(self, stats: dict, year: int, round_num: int):
        data = _jolpica_get(f"/{year}/{round_num}/results.json")
        if not data:
            stats["has_detailed_events"] = False
            return

        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        if not races:
            stats["has_detailed_events"] = False
            return

        results = races[0].get("Results", [])
        if not results:
            stats["has_detailed_events"] = False
            return

        # Winner
        p1 = results[0]
        stats["winner"] = (
            f"{p1['Driver']['givenName']} {p1['Driver']['familyName']}"
            f" ({p1.get('Constructor', {}).get('name', '')})"
        )

        # Winning margin — P2 Time.time is already a delta "+X.XXX"
        stats["winning_margin_secs"] = None
        if len(results) > 1:
            p2_time = results[1].get("Time", {}).get("time", "")
            if p2_time.startswith("+"):
                try:
                    stats["winning_margin_secs"] = float(p2_time[1:])
                except ValueError:
                    pass

        # DNFs and lapped cars
        dnf_reasons, lapped = [], 0
        for r in results:
            status = r.get("status", "")
            if _is_dnf(status):
                dnf_reasons.append(status)
            elif re.match(r"^\+\d+ Laps?$", status):
                lapped += 1

        stats["dnf_count"] = len(dnf_reasons)
        stats["dnf_reasons"] = sorted(set(dnf_reasons))
        stats["lapped_count"] = lapped
        stats["classified_finishers"] = len(results)

        # Gross position changes — proxy for overtaking
        changes = 0
        for r in results:
            try:
                grid = int(r.get("grid", 0))
                pos  = int(r.get("position", 0))
                if grid > 0 and pos > 0:
                    changes += abs(grid - pos)
            except (ValueError, TypeError):
                pass
        stats["position_changes_total"] = changes

        # Constructor diversity in top 5
        top5_teams = [r.get("Constructor", {}).get("name", "") for r in results[:5]]
        stats["top5_constructors"] = top5_teams
        stats["top5_constructor_diversity"] = len(set(top5_teams))

        # Fastest lap
        for r in results:
            fl = r.get("FastestLap", {})
            if str(fl.get("rank")) == "1":
                stats["fastest_lap"] = {
                    "driver": f"{r['Driver']['givenName']} {r['Driver']['familyName']}",
                    "time": fl.get("Time", {}).get("time", ""),
                }
                break

        # Safety car laps — not available via Ergast/Jolpica
        stats["safety_car_laps"] = None

    def _add_qualifying_stats(self, stats: dict, year: int, round_num: int):
        data = _jolpica_get(f"/{year}/{round_num}/qualifying.json")
        if not data:
            stats["has_detailed_events"] = False
            return

        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        if not races:
            stats["has_detailed_events"] = False
            return

        results = races[0].get("QualifyingResults", [])
        if not results:
            stats["has_detailed_events"] = False
            return

        pole = results[0]
        stats["pole_sitter"] = (
            f"{pole['Driver']['givenName']} {pole['Driver']['familyName']}"
            f" ({pole.get('Constructor', {}).get('name', '')})"
        )
        stats["pole_time"] = pole.get("Q3") or pole.get("Q2") or pole.get("Q1", "")

        q3_times = [_quali_time_to_secs(r.get("Q3", "")) for r in results if r.get("Q3")]
        if len(q3_times) >= 2:
            stats["q3_gap_p1_to_last_secs"] = round(max(q3_times) - min(q3_times), 3)

        top10_teams = [r.get("Constructor", {}).get("name", "") for r in results[:10]]
        stats["top10_constructors"] = top10_teams
        stats["top10_constructor_diversity"] = len(set(top10_teams))
        stats["classified_finishers"] = len(results)

    def _add_sprint_stats(self, stats: dict, year: int, round_num: int):
        data = _jolpica_get(f"/{year}/{round_num}/sprint.json")
        if not data:
            stats["has_detailed_events"] = False
            return

        races = data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
        if not races:
            stats["has_detailed_events"] = False
            return

        results = races[0].get("SprintResults", [])
        if not results:
            stats["has_detailed_events"] = False
            return

        p1 = results[0]
        stats["winner"] = (
            f"{p1['Driver']['givenName']} {p1['Driver']['familyName']}"
            f" ({p1.get('Constructor', {}).get('name', '')})"
        )

        if len(results) > 1:
            p2_time = results[1].get("Time", {}).get("time", "")
            if p2_time.startswith("+"):
                try:
                    stats["winning_margin_secs"] = float(p2_time[1:])
                except ValueError:
                    pass

        dnfs = [r for r in results if _is_dnf(r.get("status", ""))]
        stats["dnf_count"] = len(dnfs)
        stats["classified_finishers"] = len(results)

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def get_reports(self, event) -> list[str]:
        comp_name = event.event_list.name  # e.g. "Monaco Grand Prix"

        # Extract the location word(s) before "Grand Prix" as a focused keyword.
        # Falls back to the full competition name if the pattern doesn't match.
        match = re.match(r"^(.+?)\s+Grand Prix", comp_name, re.IGNORECASE)
        location = match.group(1).strip() if match else comp_name

        # Race weekend window: Thursday (3 days before) through Monday (1 day after)
        race_dt = event.date_time.replace(tzinfo=datetime.timezone.utc)
        since = race_dt - datetime.timedelta(days=3)
        until = race_dt + datetime.timedelta(days=1)

        feeds = getattr(settings, "F1_RSS_FEEDS", [])
        return fetch_matching_reports(
            feed_urls=feeds,
            keywords=[location, "Grand Prix"],
            since=since,
            until=until,
        )
