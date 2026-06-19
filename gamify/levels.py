import math

MAX_LEVEL = 50

# 7 titles spread evenly across MAX_LEVEL using integer bucketing.
# Breakpoints (level where each title starts):
#   Rookie 1, Fan 9, Regular 16, Contender 23,
#   All-Star 30, Champion 37, Legend 44
TITLES = ['Rookie', 'Fan', 'Regular', 'Contender', 'All-Star', 'Champion', 'Legend']


def xp_for_level(n):
    """Total cumulative XP required to reach level n. Level 1 costs 0 XP."""
    if n <= 1:
        return 0
    return int(100 * (n ** 1.5))


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

    if level >= MAX_LEVEL:
        return {
            'level': level,
            'title': level_title(level),
            'total_xp': total_xp,
            'xp_current': xp_current,
            'xp_next': None,
            'xp_needed': 0,
            'progress_pct': 100,
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
    }
