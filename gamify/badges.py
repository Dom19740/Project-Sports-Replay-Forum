"""
Badge-checking logic. call check_badges(user) after any XP-earning action
to award newly earned badges.

Condition functions receive (user, profile) and return bool.
They are looked up by badge slug via the _CONDITIONS registry.
"""

from core.models import Comment, Competition, Event, Rating
from .models import Badge, UserBadge, UserProfile, XPEvent


# ---------------------------------------------------------------------------
# Individual badge conditions
# ---------------------------------------------------------------------------

def _first_rating(user, profile):
    return Rating.objects.filter(voters=user).exists()


def _quick_take(user, profile):
    return XPEvent.objects.filter(user=user, action_type='event_rated_early').exists()


def _hot_streak_7(user, profile):
    return profile.longest_streak >= 7


def _hot_streak_30(user, profile):
    return profile.longest_streak >= 30


def _multi_sport_fan(user, profile):
    return (
        Event.objects.filter(rating__voters=user)
        .values('event_list_id')
        .distinct()
        .count() >= 3
    )


def _all_events_rated_in_any_comp(user, league_filter=None):
    """
    Return True if the user has rated every Event in at least one Competition.
    Optionally restrict to competitions whose league is in league_filter.
    Ignores competitions with only one event (no meaningful "weekend").
    """
    qs = Competition.objects.filter(events__rating__voters=user).distinct()
    if league_filter:
        qs = qs.filter(league__in=league_filter)

    for comp in qs:
        total = Event.objects.filter(event_list=comp).count()
        rated = Event.objects.filter(event_list=comp, rating__voters=user).count()
        if total > 1 and rated == total:
            return True
    return False


def _full_weekend(user, profile):
    return _all_events_rated_in_any_comp(user)


def _tournament_completionist(user, profile):
    return _all_events_rated_in_any_comp(
        user,
        league_filter=['FIFA World Cup', 'UEFA Champions League'],
    )


def _crowd_pleaser(user, profile):
    # Sum the likes on every event this user has rated.
    total_likes = (
        Rating.objects.filter(voters=user)
        .values_list('likes', flat=True)
    )
    return sum(total_likes) >= 50


def _commentator(user, profile):
    return Comment.objects.filter(author=user).count() >= 25


def _trusted_voice(user, profile):
    # Requires per-user star votes, which the current Rating model does not
    # store (only aggregate counts). Always returns False until a
    # UserEventRating model is added.
    # TODO: implement when individual star votes are tracked per user.
    return False


def _contrarian(user, profile):
    # Requires knowing the user's individual vote vs the consensus.
    # Not computable with the current data model.
    # TODO: implement when individual star votes are tracked per user.
    return False


# ---------------------------------------------------------------------------
# Registry — maps badge slug → condition function
# ---------------------------------------------------------------------------

_CONDITIONS = {
    'first-rating':              _first_rating,
    'quick-take':                _quick_take,
    'hot-streak-7':              _hot_streak_7,
    'hot-streak-30':             _hot_streak_30,
    'multi-sport-fan':           _multi_sport_fan,
    'full-weekend':              _full_weekend,
    'tournament-completionist':  _tournament_completionist,
    'crowd-pleaser':             _crowd_pleaser,
    'commentator':               _commentator,
    'trusted-voice':             _trusted_voice,
    'contrarian':                _contrarian,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_badges(user):
    """
    Check every un-earned badge against the user's current activity and award
    any that are newly qualified.

    Returns a (possibly empty) list of newly awarded Badge instances.
    """
    already_earned = set(
        UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
    )

    profile, _ = UserProfile.objects.get_or_create(user=user)

    newly_awarded = []

    for badge in Badge.objects.exclude(id__in=already_earned):
        condition = _CONDITIONS.get(badge.slug)
        if condition is None:
            continue
        if condition(user, profile):
            UserBadge.objects.create(user=user, badge=badge)
            newly_awarded.append(badge)

    return newly_awarded
