"""
Leaderboard query functions. Each returns a plain list of dicts so views and
templates have a stable, serialisable shape regardless of which query backed it.

Row shape:
    {
        'rank':     int,          # 1-based position
        'username': str,
        'xp':       int,          # XP relevant to this leaderboard type
        'level':    int,
        'title':    str,          # e.g. 'Rookie', 'Champion'
    }
"""

from datetime import datetime, time, timedelta

from django.contrib.auth.models import User
from django.db.models import Q, Sum

from django.utils import timezone

from .levels import level_title
from .models import UserProfile


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _row(rank, username, xp, level):
    return {
        'rank': rank,
        'username': username,
        'xp': xp,
        'level': level,
        'title': level_title(level),
    }


def _profile_level(user):
    """Return current_level from the related profile, defaulting to 1."""
    try:
        return user.profile.current_level
    except UserProfile.DoesNotExist:
        return 1


def _week_start():
    today = timezone.now().date()
    return timezone.make_aware(
        datetime.combine(today - timedelta(days=today.weekday()), time.min)
    )


def _month_start():
    today = timezone.now().date()
    return timezone.make_aware(
        datetime.combine(today.replace(day=1), time.min)
    )


# ---------------------------------------------------------------------------
# Public query functions
# ---------------------------------------------------------------------------

def global_alltime(limit=50):
    """
    Rank users by their stored total_xp (read directly from UserProfile —
    no aggregation needed).
    """
    profiles = (
        UserProfile.objects
        .select_related('user')
        .order_by('-total_xp')[:limit]
    )
    return [
        _row(rank, p.user.username, p.total_xp, p.current_level)
        for rank, p in enumerate(profiles, start=1)
    ]


def global_period(period, limit=50):
    """
    Rank users by XP earned during 'week' or 'month', summed from XPEvent
    timestamps. Users with zero XP in the period are excluded.
    """
    since = _week_start() if period == 'week' else _month_start()

    users = (
        User.objects
        .annotate(
            period_xp=Sum(
                'xp_events__amount',
                filter=Q(xp_events__created__gte=since),
            )
        )
        .filter(period_xp__gt=0)
        .select_related('profile')
        .order_by('-period_xp')[:limit]
    )
    return [
        _row(rank, u.username, u.period_xp, _profile_level(u))
        for rank, u in enumerate(users, start=1)
    ]


def sport_leaderboard(league, limit=50):
    """
    Rank users by XP earned from actions whose related_event belongs to the
    given league (Competition.league). Includes star ratings, likes, comments,
    and any bonuses tied to events in that sport.
    """
    users = (
        User.objects
        .annotate(
            sport_xp=Sum(
                'xp_events__amount',
                filter=Q(xp_events__related_event__event_list__league=league),
            )
        )
        .filter(sport_xp__gt=0)
        .select_related('profile')
        .order_by('-sport_xp')[:limit]
    )
    return [
        _row(rank, u.username, u.sport_xp, _profile_level(u))
        for rank, u in enumerate(users, start=1)
    ]


def competition_leaderboard(competition_id, limit=50):
    """
    Rank users by XP earned from actions on events within one specific
    Competition (e.g. the 2024 British Grand Prix).
    """
    users = (
        User.objects
        .annotate(
            comp_xp=Sum(
                'xp_events__amount',
                filter=Q(xp_events__related_event__event_list_id=competition_id),
            )
        )
        .filter(comp_xp__gt=0)
        .select_related('profile')
        .order_by('-comp_xp')[:limit]
    )
    return [
        _row(rank, u.username, u.comp_xp, _profile_level(u))
        for rank, u in enumerate(users, start=1)
    ]
