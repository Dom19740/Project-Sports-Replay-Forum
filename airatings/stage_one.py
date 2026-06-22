import json
import logging
from airatings.llm_client import complete

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

# (type, min_inclusive, max_inclusive)  — None means no bound
_INT_FIELDS: dict[str, tuple[int, int]] = {
    "excitement":      (1, 5),
    "drama":           (1, 5),
    "competitiveness": (1, 5),
    "late_tension":    (1, 5),
    "controversy":     (0, 3),
    "lead_changes":    (0, 50),
}
_BOOL_FIELDS = {"had_late_decisive_moment"}
_STR_FIELDS  = {"one_line_internal_note"}
_ALL_FIELDS  = set(_INT_FIELDS) | _BOOL_FIELDS | _STR_FIELDS


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM = """\
You are a sports entertainment analyst. Given structured event statistics and press report \
snippets, extract excitement signals for a completed sporting event.

Rate based on entertainment and tension value for a NEUTRAL viewer who has no attachment \
to either side. Higher numbers = more entertaining.

Output ONLY a valid JSON object — no markdown, no prose, no comments. Exactly these keys:

{
  "excitement":               <int 1-5>,
  "drama":                    <int 1-5>,
  "competitiveness":          <int 1-5>,
  "late_tension":             <int 1-5>,
  "controversy":              <int 0-3>,
  "lead_changes":             <int, infer from available data>,
  "had_late_decisive_moment": <bool>,
  "one_line_internal_note":   "<private one-sentence note — may include names, scores, incidents>"
}

Definitions:
- excitement: overall entertainment value
- drama: narrative arc, turning points, swings, unpredictability
- competitiveness: how close and contested the event was
- late_tension: how decisive and tense the final phase was
- controversy: disputed incidents, contentious calls, flashpoints (0=none, 1=minor, 2=notable, 3=high)
- lead_changes: times the lead changed hands (infer; use 0 if dominant from the start)
- had_late_decisive_moment: key moment in the final 20% of the event
- one_line_internal_note: private analyst note for pipeline use; NEVER shown to users

CALIBRATION RULES — apply these before scoring, without exception:

excitement (anchored to scoring density for football; action density for F1/motorsport):
  Football:
    7+ total goals  → excitement MUST be 5
    5-6 total goals → excitement MUST be ≥ 4
    3-4 total goals → excitement is typically 3-4 (adjust for flow and shots)
    0-2 total goals → excitement is typically 1-3 (adjust upward for high xg/shots)
  Motorsport: weight DNFs, safety cars, on-track position changes, and wet conditions heavily.

F1/Motorsport — late_tension and had_late_decisive_moment:
  The stats include a "late_retirements" list: retirements that occurred in the final 20% of race
  distance, each with "race_pct" (e.g. 0.924 = 92.4% race distance).
  "championship_leader_dnf_race_pct" gives the exact moment the points leader retired.

  Apply these rules without exception:
    late_retirements is non-empty               → had_late_decisive_moment MUST be True
                                                   late_tension MUST be ≥ 4
    championship_leader_dnf_race_pct ≥ 0.80    → drama MUST be ≥ 4
                                                   This is a defining championship moment.
    championship_leader_dnf_race_pct ≥ 0.90    → drama MUST be 5
                                                   A leader retiring in the final 10% is
                                                   the highest narrative impact possible.
    winning_margin_secs alone does NOT determine late_tension:
      A dominant winner with a large gap can still have high late_tension if retirements,
      safety cars, or battles behind occurred in the final laps.

competitiveness (reflects actual on-track closeness — NOT team reputation or pre-match billing):
  Final margin 0 (draw)   → competitiveness 4-5
  Final margin 1           → competitiveness 3-4
  Final margin 2-3         → competitiveness 2-3
  Final margin 4+          → competitiveness 1-2
  A 7-1 result is NOT competitive (score 1-2) even if both teams are well-known.
  A 0-0 draw with high xg IS competitive (score 4-5) even between unfancied teams.

CRITICAL — team/driver bias is forbidden:
  Do NOT adjust any score based on team names, driver fame, nationality, or historical prestige.
  Do NOT inflate scores because the match is a "marquee" fixture or involves famous competitors.
  Rate only what actually happened during the event.\
"""


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _validate(data: dict) -> list[str]:
    """Return a list of error strings. Empty list = valid."""
    errors = []

    missing = _ALL_FIELDS - set(data)
    for f in sorted(missing):
        errors.append(f"Missing field: {f!r}")

    for field, (lo, hi) in _INT_FIELDS.items():
        if field not in data:
            continue
        val = data[field]
        # Coerce float integers (e.g. 4.0 → 4)
        if isinstance(val, float) and val.is_integer():
            data[field] = val = int(val)
        if not isinstance(val, int) or isinstance(val, bool):
            errors.append(f"{field!r}: expected int, got {type(val).__name__} ({val!r})")
            continue
        if not (lo <= val <= hi):
            errors.append(f"{field!r}={val} out of range [{lo}, {hi}]")

    for field in _BOOL_FIELDS:
        if field not in data:
            continue
        val = data[field]
        # Coerce int 0/1 to bool
        if isinstance(val, int) and not isinstance(val, bool):
            data[field] = bool(val)
        elif not isinstance(val, bool):
            errors.append(f"{field!r}: expected bool, got {type(val).__name__} ({val!r})")

    for field in _STR_FIELDS:
        if field not in data:
            continue
        if not isinstance(data[field], str):
            errors.append(f"{field!r}: expected str, got {type(data[field]).__name__}")

    return errors


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def extract_signals(stats: dict, reports: list[str]) -> dict:
    """
    Stage one: spoiler-full signal extraction.
    Calls the LLM twice at most. Raises RuntimeError if both attempts fail validation.
    """
    user_parts = [f"STATS:\n{json.dumps(stats, indent=2, default=str)}"]
    if reports:
        joined = "\n\n---\n\n".join(reports)
        user_parts.append(f"PRESS REPORTS:\n{joined}")
    user_msg = "\n\n".join(user_parts)

    for attempt in range(1, 3):
        try:
            raw = complete(_SYSTEM, user_msg, json_mode=True)
        except Exception as exc:
            logger.error("stage_one LLM call failed (attempt %d): %s", attempt, exc)
            if attempt == 2:
                raise RuntimeError(f"LLM call failed after 2 attempts: {exc}") from exc
            continue

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.error("stage_one: invalid JSON on attempt %d — %s\nRaw: %s", attempt, exc, raw[:500])
            if attempt == 2:
                raise RuntimeError(f"LLM returned non-JSON after 2 attempts") from exc
            continue

        errors = _validate(data)
        if not errors:
            return data

        logger.warning(
            "stage_one: schema errors on attempt %d:\n%s\nRaw: %s",
            attempt,
            "\n".join(f"  • {e}" for e in errors),
            raw[:500],
        )
        if attempt == 2:
            raise RuntimeError(
                f"extract_signals failed schema validation after 2 attempts.\n"
                + "\n".join(errors)
            )

    # Unreachable, but keeps linters happy
    raise RuntimeError("extract_signals: unexpected exit")
