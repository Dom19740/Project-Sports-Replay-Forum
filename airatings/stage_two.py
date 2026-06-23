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
You are an enthusiastic but professional sports commentator giving a spoiler-free \
verdict on whether an event is worth watching. Write 1-2 sentences (30-45 words) \
that feel warm and genuine — like a knowledgeable fan, not a journalist filing copy \
and not a mate sending a text.

Strict rules:
- Do NOT name any team, player, driver, circuit, country, city, or competition.
- Do NOT state or imply who won, lost, drew, finished ahead, or finished behind.
- Do NOT mention any scoreline, goal tally, time, minute, lap, or round.
- Do NOT describe a specific incident (no "a penalty", "a crash", "a red card", \
"a late goal", "an overtake").
- Banned words and phrases: won, beat, defeated, lost, drew, comeback, \
lead, leads, led, ahead, behind, equalised, equalized, winner, loser, \
champion, podium, first, second, third, proceedings, unfolded, momentum, \
narrative, encounter, contest, spectacle, predictably, predictable, \
one-sided, straightforward, comfortable, comfortably, dominated, dominant, \
as expected, went as expected, surprise, surprisingly, upset, underdog.
- NEVER imply how the result compared to expectations — do not suggest \
it was a surprise or that it went to form. Only describe entertainment \
value in absolute terms (was it tense and exciting, or flat and dull).
- Use plain, natural language — avoid both tabloid slang and stiff formal phrasing.
- No exclamation marks unless the event is genuinely exceptional (5/5 signals).
- No filler openers like "Dude", "Honestly", "Look", or "Right".
- Calibrate energy to match the signal numbers — a 5/5 event sounds \
like something you can't miss; a 1/5 event sounds like one to skip.
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
