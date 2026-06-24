MAX_LEVEL = 25

# 7 titles spread evenly across MAX_LEVEL using integer bucketing.
# Breakpoints (level where each title starts):
#   Rookie 1, Fan 5, Regular 9, Contender 12,
#   All-Star 16, Champion 19, Legend 23
TITLES = ['Rookie', 'Fan', 'Regular', 'Contender', 'All-Star', 'Champion', 'Legend']

# (min_level, bg_color, text_color) — last matching entry wins.
_STAGE_COLORS = [
    (1,  '#888888', '#fff'),   # Rookie
    (5,  '#24e4e7', '#000'),   # Fan
    (9,  '#95d0bb', '#000'),   # Regular
    (12, '#f6933f', '#000'),   # Contender
    (16, '#f37484', '#fff'),   # All-Star
    (19, '#ee35b9', '#fff'),   # Champion
    (23, '#FFD700', '#000'),   # Legend
]


# Gradient stops that the XP bar sweeps through (matches CSS in xp_strip).
_XP_GRADIENT = [
    (0,   (0x24, 0xe4, 0xe7)),
    (20,  (0x95, 0xd0, 0xbb)),
    (40,  (0xf6, 0x93, 0x3f)),
    (60,  (0xf3, 0x74, 0x84)),
    (80,  (0xee, 0x35, 0xb9)),
    (100, (0xFF, 0xD7, 0x00)),
]


def xp_gradient_color(pct):
    """Return the hex colour at position pct (0-100) along the XP bar gradient."""
    pct = max(0, min(100, pct))
    for i in range(len(_XP_GRADIENT) - 1):
        p1, c1 = _XP_GRADIENT[i]
        p2, c2 = _XP_GRADIENT[i + 1]
        if pct <= p2:
            t = (pct - p1) / (p2 - p1) if p2 > p1 else 0
            r = round(c1[0] + (c2[0] - c1[0]) * t)
            g = round(c1[1] + (c2[1] - c1[1]) * t)
            b = round(c1[2] + (c2[2] - c1[2]) * t)
            return f'#{r:02x}{g:02x}{b:02x}'
    last = _XP_GRADIENT[-1][1]
    return f'#{last[0]:02x}{last[1]:02x}{last[2]:02x}'


def level_colors(level):
    """Return (bg_color, text_color) for the given level."""
    bg, text = _STAGE_COLORS[0][1], _STAGE_COLORS[0][2]
    for threshold, b, t in _STAGE_COLORS:
        if level >= threshold:
            bg, text = b, t
    return bg, text


def xp_for_level(n):
    """Total cumulative XP required to reach level n. Level 1 costs 0 XP."""
    if n <= 1:
        return 0
    return int(9 * (n ** 1.5))


def compute_level(total_xp):
    """Return the level for a given total_xp value, capped at MAX_LEVEL."""
    level = 1
    while level < MAX_LEVEL and total_xp >= xp_for_level(level + 1):
        level += 1
    return level


def level_title(level):
    """Return the title string for a given level number."""
    idx = min((level - 1) * len(TITLES) // MAX_LEVEL, len(TITLES) - 1)
    return TITLES[idx]


def level_info(profile):
    """
    Return a dict describing the user's current level state:

      level        — current level (int)
      title        — title for this level ('Rookie' … 'Legend')
      total_xp     — the user's total XP
      xp_current   — XP threshold at the start of this level
      xp_next      — XP threshold for the next level (None at MAX_LEVEL)
      xp_needed    — XP still needed to reach the next level (0 at MAX_LEVEL)
      progress_pct — 0-100 integer progress bar value toward next level
    """
    level = profile.current_level
    total_xp = profile.total_xp
    xp_current = xp_for_level(level)

    bg, text = level_colors(level)

    if level >= MAX_LEVEL:
        return {
            'level': level,
            'title': level_title(level),
            'total_xp': total_xp,
            'xp_current': xp_current,
            'xp_next': None,
            'xp_needed': 0,
            'progress_pct': 100,
            'bg_color': bg,
            'text_color': text,
        }

    xp_next = xp_for_level(level + 1)
    span = xp_next - xp_current
    earned_in_level = total_xp - xp_current
    progress_pct = min(100, int(earned_in_level * 100 / span))

    return {
        'level': level,
        'title': level_title(level),
        'total_xp': total_xp,
        'xp_current': xp_current,
        'xp_next': xp_next,
        'xp_needed': xp_next - total_xp,
        'progress_pct': progress_pct,
        'bg_color': bg,
        'text_color': text,
    }
