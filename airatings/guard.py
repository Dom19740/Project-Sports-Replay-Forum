import re
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Result-indicating words (whole-word match, case-insensitive)
# ---------------------------------------------------------------------------

_RESULT_VERBS = frozenset({
    # Win / loss / draw
    "won", "win", "wins",
    "beat", "beats",
    "defeated", "defeats",
    "lost", "lose", "loses",
    "drew", "draw", "draws",
    # Outcome synonyms
    "equalised", "equalized", "equalises", "equalizes",
    "scored", "scores",
    "winner", "loser",
    "champion", "champions",
    "victory", "victories",
    # Narrative / structure
    "comeback",
    "podium",
    # Score word
    "nil",
})

# ---------------------------------------------------------------------------
# Banned sub-string phrases (full blurb, case-insensitive)
# ---------------------------------------------------------------------------

_BANNED_PHRASES = (
    "came from behind",
    "come from behind",
    "take the lead",
    "took the lead",
    "in the lead",
    "ran out",
    "came back from",
)

# ---------------------------------------------------------------------------
# Scoreline detection
# ---------------------------------------------------------------------------

_DIGIT_SCORE_RE = re.compile(r'\b\d+\s*[-–—]\s*\d+\b')

_NUMBER_WORDS = frozenset({
    "zero", "one", "two", "three", "four", "five",
    "six", "seven", "eight", "nine", "ten", "nought",
})

_SCORE_CONTEXTS = frozenset({"goal", "goals", "point", "points"})

_WRITTEN_SCORE_RE = re.compile(
    r'\b(' + '|'.join(sorted(_NUMBER_WORDS)) + r')\s+(' + '|'.join(sorted(_SCORE_CONTEXTS)) + r')\b',
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# League constants
# ---------------------------------------------------------------------------

_FOOTBALL_LEAGUES = {"FIFA World Cup", "English Premier League"}
_F1_LEAGUES       = {"Formula 1"}

# Words too generic to ban as standalone tokens
_GENERIC_WORDS = frozenset({
    "grand", "prix", "gp", "the", "and", "for", "de", "le", "la",
    "cup", "world", "league", "premier", "english", "formula", "race",
    "international",
})

_MIN_TOKEN_LEN = 4  # skip "fc", "vs", "de", etc.


# ---------------------------------------------------------------------------
# Name extraction helpers
# ---------------------------------------------------------------------------

def _significant_tokens(text: str) -> set[str]:
    """Break a name string into meaningful lowercase tokens (len ≥ MIN_TOKEN_LEN)."""
    tokens = set()
    for word in re.split(r"[\s\-\/]+", text.lower()):
        if word and len(word) >= _MIN_TOKEN_LEN and word not in _GENERIC_WORDS:
            tokens.add(word)
    return tokens


def _extract_football_names(event) -> set[str]:
    """
    Build the name set for a football event:
    • National team names — parsed directly from event.event_type ("Spain vs Cape Verde")
    • Player last names   — from TheSportsDB lookuplineup (already cached from stage-one)
    """
    names: set[str] = set()

    # National team names live in event_type as "Home vs Away"
    if " vs " in event.event_type:
        home, away = event.event_type.split(" vs ", 1)
        for team in (home.strip(), away.strip()):
            names.add(team.lower())          # full phrase
            names.update(_significant_tokens(team))

    # Player names from lineup (cached — no extra API cost)
    try:
        from airatings.ingest.football import _sportsdb_fetch  # noqa: PLC0415
        lineup_data = _sportsdb_fetch("lookuplineup.php", event.idEvent)
        for player in (lineup_data or {}).get("lineup") or []:
            full = player.get("strPlayer", "")
            if not full:
                continue
            names.add(full.lower())
            parts = full.split()
            if len(parts) > 1:
                last = parts[-1].lower()
                if len(last) >= _MIN_TOKEN_LEN:
                    names.add(last)
    except Exception as exc:
        logger.debug("guard: football lineup fetch skipped: %s", exc)

    return names


def _extract_f1_names(event) -> set[str]:
    """
    Build the name set for an F1 event:
    • Circuit / location tokens from event_list.name
    • Driver last names and constructor names from cached Jolpica results
    """
    names: set[str] = set()
    names.update(_significant_tokens(event.event_list.name))

    try:
        from airatings.ingest.f1 import F1DataSource, _jolpica_get  # noqa: PLC0415
        year = event.date_time.year
        round_num = F1DataSource()._find_round(year, event.event_list.name)
        if round_num:
            data = _jolpica_get(f"/{year}/{round_num}/results.json")
            races = (data or {}).get("MRData", {}).get("RaceTable", {}).get("Races", [])
            for result in (races[0].get("Results", []) if races else []):
                driver = result.get("Driver", {})
                for part in (driver.get("givenName", ""), driver.get("familyName", "")):
                    if part and len(part) >= _MIN_TOKEN_LEN:
                        names.add(part.lower())
                constructor = result.get("Constructor", {}).get("name", "")
                if constructor:
                    names.add(constructor.lower())
                    names.update(_significant_tokens(constructor))
    except Exception as exc:
        logger.debug("guard: F1 name extraction skipped: %s", exc)

    return names


def _build_banned_names(event) -> set[str]:
    """Full banned-entity set for this event."""
    names = _significant_tokens(event.event_list.name)
    if event.event_list.league in _FOOTBALL_LEAGUES:
        names.update(_extract_football_names(event))
    elif event.event_list.league in _F1_LEAGUES:
        names.update(_extract_f1_names(event))
    return names


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def check_blurb(blurb: str, event) -> tuple[bool, list[str]]:
    """
    Inspect a blurb for spoiler leaks.

    Returns (is_safe, reasons).  Empty reasons list → safe.
    Bias: flag aggressively — one real leak is a feature failure.
    """
    reasons: list[str] = []
    blurb_lower = blurb.lower()
    blurb_words = set(re.findall(r"\b[a-z]+\b", blurb_lower))

    # 1. Result verbs / outcome words
    for word in sorted(_RESULT_VERBS & blurb_words):
        reasons.append(f"result verb: '{word}'")

    # 2. Digit scoreline  e.g. "3-1", "2–0"
    for match in _DIGIT_SCORE_RE.finditer(blurb):
        reasons.append(f"digit scoreline: '{match.group()}'")

    # 3. Written score  e.g. "two goals", "three points"
    for match in _WRITTEN_SCORE_RE.finditer(blurb):
        reasons.append(f"written score: '{match.group()}'")

    # 4. Banned phrases
    for phrase in _BANNED_PHRASES:
        if phrase in blurb_lower:
            reasons.append(f"banned phrase: '{phrase}'")

    # 5. Named entities (teams, players, drivers, circuits)
    banned_names = _build_banned_names(event)
    for name in sorted(banned_names):
        if " " in name:  # multi-word phrase
            if name in blurb_lower:
                reasons.append(f"named entity: '{name}'")
        else:
            if name in blurb_words:
                reasons.append(f"named entity: '{name}'")

    is_safe = not reasons
    if not is_safe:
        logger.warning(
            "guard: event pk=%s — %d issue(s): %s",
            getattr(event, "pk", "?"),
            len(reasons),
            "; ".join(reasons),
        )
    return is_safe, reasons


def run_with_guard(signals: dict, verdict: dict, event) -> tuple[str, bool, list[str]]:
    """
    Full blurb pipeline: stage-two generation + guard check, with one regeneration attempt.

    Returns:
        (blurb, is_safe, reasons)
        is_safe=False → requires manual review; reasons explains why.
    """
    from airatings.stage_two import write_blurb  # lazy import avoids circular dependency

    last_blurb = ""
    last_reasons: list[str] = []

    for attempt in range(1, 3):
        blurb = write_blurb(signals, verdict)
        is_safe, reasons = check_blurb(blurb, event)
        last_blurb = blurb
        last_reasons = reasons

        if is_safe:
            if attempt == 2:
                logger.info("guard: passed on retry for event pk=%s", getattr(event, "pk", "?"))
            return blurb, True, []

        logger.warning(
            "guard: attempt %d failed for event pk=%s — %s",
            attempt,
            getattr(event, "pk", "?"),
            "; ".join(reasons),
        )

    logger.error(
        "guard: MANUAL REVIEW REQUIRED — event pk=%s | blurb: %r | reasons: %s",
        getattr(event, "pk", "?"),
        last_blurb,
        "; ".join(last_reasons),
    )
    return last_blurb, False, last_reasons
