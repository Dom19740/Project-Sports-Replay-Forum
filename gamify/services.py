from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .levels import compute_level, level_title
from .models import UserProfile, XPEvent

# XP awarded for each action type.
# event_rated_early is a bonus on top of event_rated, not a standalone action.
XP_VALUES = {
    'event_rated':       5,
    'event_rated_early': 5,   # bonus: rated within 1 hour of event finishing
    'event_liked':       1,   # you liked/disliked an event
    'rating_liked':      3,   # your event rating received a like
    'comment_posted':    4,
    'comment_liked':     2,   # your comment received a like
    'daily_bonus':       5,   # first qualifying action of the day
    'reply_posted':      0,   # not awarded yet; hook is wired, value is 0
    'badge_awarded':     0,   # caller supplies amount via xp_override
}

# Only actions the user actively performs count toward the daily streak and
# trigger the daily bonus. Passive rewards (comment_liked, rating_liked) and
# secondary awards (daily_bonus, event_rated_early, badge_awarded) are excluded.
STREAK_QUALIFYING_ACTIONS = frozenset({
    'event_rated',
    'comment_posted',
    'reply_posted',
    'event_liked',
})

# Diminishing returns config per action type.
#
# 'full' = daily occurrences that earn 100% XP  (occurrences 0 .. full-1)
# 'half' = daily occurrences that earn 50%  XP  (occurrences full .. half-1)
# Beyond 'half'               → 25% (minimum 1 XP)
#
# Actions absent from this dict are never tapered (daily_bonus, badge_awarded,
# event_rated_early — these are already self-limiting by design).
_DIMINISHING = {
    'event_rated':    {'full':  5, 'half': 10},
    'event_liked':    {'full': 10, 'half': 25},
    'rating_liked':   {'full': 10, 'half': 25},
    'comment_posted': {'full':  5, 'half': 15},
    'comment_liked':  {'full': 10, 'half': 25},
    'reply_posted':   {'full':  5, 'half': 15},
}

_EARLY_RATING_WINDOW = timedelta(hours=2)


def _tapered_amount(action_type, base_amount, daily_count):
    """
    Returns the XP for the Nth daily occurrence of action_type.
    daily_count is occurrences already logged today (before this one).
    """
    config = _DIMINISHING.get(action_type)
    if config is None or base_amount <= 0:
        return base_amount
    if daily_count < config['full']:
        return base_amount
    if daily_count < config['half']:
        return max(1, base_amount // 2)
    return max(1, base_amount // 4)


def _resolve_related(related_object):
    """Return (related_event, related_comment) from an arbitrary related object."""
    from core.models import Event, Comment  # local import avoids circular dependency
    if isinstance(related_object, Event):
        return related_object, None
    if isinstance(related_object, Comment):
        return related_object.event, related_object
    return None, None


def _qualifies_for_early_bonus(event):
    return (
        event is not None
        and event.is_finished
        and (timezone.now() - event.date_time) < _EARLY_RATING_WINDOW
    )


def _update_streak(profile, today):
    """
    Advance the streak for a qualifying action taken on `today`.

    Called only when this is the first qualifying action of the day, so
    `profile.last_active_date` is guaranteed to be before today here.

    - Consecutive day: increment current_streak.
    - Gap of one or more days: reset current_streak to 0 first, then increment.
      (Streak-freeze logic would replace the reset here when implemented.)
    - Always update longest_streak and last_active_date.
    """
    yesterday = today - timedelta(days=1)

    if profile.last_active_date != yesterday:
        # One or more days missed — streak is broken.
        # TODO: check for an active streak freeze before resetting.
        profile.current_streak = 0

    profile.current_streak += 1

    if profile.current_streak > profile.longest_streak:
        profile.longest_streak = profile.current_streak

    profile.last_active_date = today


def award_xp(user, action_type, related_object=None, xp_override=None):
    """
    Central XP-awarding function. Every XP-earning action in the codebase
    must go through here.

    - Creates one XPEvent per award (primary + any bonuses).
    - Updates UserProfile.total_xp and current_level.
    - On the first *qualifying* action of a new calendar day, advances the
      daily streak and awards the daily bonus.
    - Applies diminishing returns to high-volume actions.

    Returns the total XP awarded in this call.
    """
    base_amount = xp_override if xp_override is not None else XP_VALUES.get(action_type, 0)
    related_event, related_comment = _resolve_related(related_object)

    with transaction.atomic():
        profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)
        old_level = profile.current_level

        today = timezone.now().date()

        # Streak and daily bonus only fire on actively performed actions.
        is_qualifying = action_type in STREAK_QUALIFYING_ACTIONS
        is_first_qualifying_today = is_qualifying and profile.last_active_date != today

        # Count how many times this action_type has already been logged today,
        # then apply the taper to the base amount.
        daily_count = XPEvent.objects.filter(
            user=user,
            action_type=action_type,
            created__date=today,
        ).count()
        amount = _tapered_amount(action_type, base_amount, daily_count)

        awards = [(action_type, amount)]

        if action_type == 'event_rated' and _qualifies_for_early_bonus(related_event):
            awards.append(('event_rated_early', XP_VALUES['event_rated_early']))

        if is_first_qualifying_today:
            awards.append(('daily_bonus', XP_VALUES['daily_bonus']))

        total_xp = sum(amt for _, amt in awards)

        XPEvent.objects.bulk_create([
            XPEvent(
                user=user,
                action_type=at,
                amount=amt,
                related_event=related_event,
                related_comment=related_comment,
            )
            for at, amt in awards
        ])

        if is_first_qualifying_today:
            _update_streak(profile, today)

        profile.total_xp += total_xp
        profile.current_level = compute_level(profile.total_xp)
        profile.save(update_fields=[
            'total_xp', 'current_level',
            'current_streak', 'longest_streak', 'last_active_date',
        ])

    return {
        'xp': total_xp,
        'leveled_up': profile.current_level > old_level,
        'new_level': profile.current_level,
        'new_title': level_title(profile.current_level),
    }
