import logging
from airatings.llm_client import complete

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# The only signal keys that may ever be forwarded to stage two.
# one_line_internal_note is deliberately excluded — it contains spoiler content.
# ---------------------------------------------------------------------------

_SAFE_SIGNAL_KEYS = (
    "excitement",
    "drama",
    "competitiveness",
    "late_tension",
    "controversy",
    "lead_changes",
    "had_late_decisive_moment",
)

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM = """\
You are a spoiler-free sports writer. Write a single blurb of 1-2 sentences \
(30-45 words) that tells a neutral viewer whether this event is worth watching \
— without revealing any outcome, score, or specific detail.

Strict rules:
- Do NOT name any team, player, driver, circuit, country, city, or competition.
- Do NOT state or imply who won, lost, drew, finished ahead, or finished behind.
- Do NOT mention any scoreline, goal tally, time, minute, lap, or round.
- Do NOT describe a specific incident (no "a penalty", "a crash", "a red card", \
"a late goal", "an overtake").
- Banned words and phrases: won, beat, defeated, lost, drew, comeback, \
lead, leads, led, ahead, behind, equalised, equalized, winner, loser, \
champion, podium, first, second, third.
- Write about emotional shape only: atmosphere, tension, drama, momentum, \
unpredictability, competitiveness.
- Calibrate intensity to match the signal numbers — a 5/5 event sounds \
urgent and unmissable; a 1/5 event sounds flat and skippable.
- Output only the blurb. No title, no label, no quotes, no markdown.\
"""


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def write_blurb(signals: dict, verdict: dict) -> str:
    """
    Stage two: spoiler-free blurb generation.

    Receives ONLY numeric/bool signals and the verdict dict.
    Never receives stats, reports, names, scores, or one_line_internal_note.
    """
    # Strip to only the safe keys — the model cannot leak what it never receives
    safe = {k: signals[k] for k in _SAFE_SIGNAL_KEYS if k in signals}

    stars   = verdict.get("stars",   "?")
    verdict_label = verdict.get("verdict", "unknown")

    user_msg = (
        f"ENTERTAINMENT SIGNALS (numeric scales as defined):\n"
        f"  excitement:               {safe.get('excitement', '?')}/5\n"
        f"  drama:                    {safe.get('drama', '?')}/5\n"
        f"  competitiveness:          {safe.get('competitiveness', '?')}/5\n"
        f"  late_tension:             {safe.get('late_tension', '?')}/5\n"
        f"  controversy:              {safe.get('controversy', '?')}/3\n"
        f"  momentum_swings:          {safe.get('lead_changes', 0)}\n"
        f"  decisive_late_moment:     {str(safe.get('had_late_decisive_moment', False)).lower()}\n"
        f"\n"
        f"VERDICT: {verdict_label} ({stars}★)\n"
        f"\n"
        f"Write the spoiler-free blurb now."
    )

    try:
        blurb = complete(_SYSTEM, user_msg, json_mode=False).strip()
    except Exception as exc:
        logger.error("stage_two LLM call failed: %s", exc)
        raise RuntimeError(f"write_blurb failed: {exc}") from exc

    return blurb
