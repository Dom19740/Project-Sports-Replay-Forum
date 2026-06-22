# ---------------------------------------------------------------------------
# Weights (must sum to 1.0)
# ---------------------------------------------------------------------------

W_EXCITEMENT      = 0.30
W_DRAMA           = 0.25
W_LATE_TENSION    = 0.25
W_COMPETITIVENESS = 0.20

# ---------------------------------------------------------------------------
# Bonus values (added on top of the weighted base)
# ---------------------------------------------------------------------------

BONUS_LATE_DECISIVE   = 0.35   # had_late_decisive_moment == True
BONUS_PER_CONTROVERSY = 0.35   # multiplied by controversy (0-3), max +1.05
BONUS_PER_LEAD_CHANGE = 0.10   # multiplied by min(lead_changes, 3), max +0.30

# ---------------------------------------------------------------------------
# Scoring bounds
# ---------------------------------------------------------------------------

SCORE_MIN = 1.0
SCORE_MAX = 5.0

# ---------------------------------------------------------------------------
# Stars thresholds — (lower_bound_inclusive, stars)
# Evaluated top-to-bottom; first match wins.
# ---------------------------------------------------------------------------

STARS_THRESHOLDS = [
    (4.5, 5),
    (3.5, 4),
    (2.5, 3),
    (1.5, 2),
    (0.0, 1),
]

# ---------------------------------------------------------------------------
# Verdict bands
# ---------------------------------------------------------------------------

VERDICT_HOT = "hot_watch"
VERDICT_MID = "mid_temp"
VERDICT_NOT = "not_watch"

HOT_WATCH_MIN_STARS = 4  # 4★ and 5★ → hot_watch
MID_TEMP_MIN_STARS  = 3  # 3★       → mid_temp
                          # 1-2★     → not_watch


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def map_to_verdict(signals: dict) -> dict:
    """
    Deterministic, LLM-free mapping from stage-one signals to a user verdict.

    Returns:
        stars (int 1-5), verdict (str), rationale_internal (str)
    """
    # --- Weighted base score (scale: 1–5) --------------------------------
    base = (
        signals.get("excitement",      1) * W_EXCITEMENT      +
        signals.get("drama",           1) * W_DRAMA           +
        signals.get("late_tension",    1) * W_LATE_TENSION    +
        signals.get("competitiveness", 1) * W_COMPETITIVENESS
    )

    # --- Bonuses ----------------------------------------------------------
    bonus_breakdown: list[str] = []

    bonus = 0.0
    if signals.get("had_late_decisive_moment", False):
        bonus += BONUS_LATE_DECISIVE
        bonus_breakdown.append(f"late_decisive=+{BONUS_LATE_DECISIVE:.2f}")

    con = int(signals.get("controversy", 0))
    if con:
        con_bonus = con * BONUS_PER_CONTROVERSY
        bonus += con_bonus
        bonus_breakdown.append(f"controversy({con})=+{con_bonus:.2f}")

    lc = min(int(signals.get("lead_changes", 0)), 3)
    if lc:
        lc_bonus = lc * BONUS_PER_LEAD_CHANGE
        bonus += lc_bonus
        bonus_breakdown.append(f"lead_changes({lc})=+{lc_bonus:.2f}")

    # --- Final score ------------------------------------------------------
    raw_score = base + bonus
    score = max(SCORE_MIN, min(SCORE_MAX, raw_score))

    # --- Stars ------------------------------------------------------------
    stars = 1
    for threshold, star_value in STARS_THRESHOLDS:
        if score >= threshold:
            stars = star_value
            break

    # --- Verdict ----------------------------------------------------------
    if stars >= HOT_WATCH_MIN_STARS:
        verdict = VERDICT_HOT
    elif stars >= MID_TEMP_MIN_STARS:
        verdict = VERDICT_MID
    else:
        verdict = VERDICT_NOT

    # --- Rationale --------------------------------------------------------
    bonus_str = ", ".join(bonus_breakdown) if bonus_breakdown else "none"
    rationale_internal = (
        f"base={base:.2f} "
        f"[exc:{signals.get('excitement',1)}×{W_EXCITEMENT} "
        f"dra:{signals.get('drama',1)}×{W_DRAMA} "
        f"lat:{signals.get('late_tension',1)}×{W_LATE_TENSION} "
        f"comp:{signals.get('competitiveness',1)}×{W_COMPETITIVENESS}] "
        f"+ bonus={bonus:.2f} [{bonus_str}] "
        f"→ score={score:.2f} → {stars}★ → {verdict}"
    )

    return {
        "stars":              stars,
        "verdict":            verdict,
        "rationale_internal": rationale_internal,
    }
