from django.db import models
from django.contrib.auth.models import User

from .levels import compute_level  # noqa: F401 — re-exported for services.py


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_xp = models.IntegerField(default=0)
    current_level = models.IntegerField(default=1)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} — Level {self.current_level} ({self.total_xp} XP)'


class XPEvent(models.Model):
    ACTION_TYPES = [
        ('comment_posted',    'Posted a comment'),
        ('reply_posted',      'Posted a reply'),
        ('event_rated',       'Rated an event'),
        ('event_rated_early', 'Rated within 1 hour of event finishing (bonus)'),
        ('event_liked',       'Liked/disliked an event'),
        ('rating_liked',      'Your event rating received a like'),
        ('comment_liked',     'Comment received a like'),
        ('daily_bonus',       'First action of the day'),
        ('badge_awarded',     'Badge unlocked'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='xp_events')
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    amount = models.IntegerField()
    related_event = models.ForeignKey(
        'core.Event', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='xp_events',
    )
    related_comment = models.ForeignKey(
        'core.Comment', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='xp_events',
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.user.username} +{self.amount} XP ({self.action_type})'


class Badge(models.Model):
    RARITY_CHOICES = [
        (1, 'Common'),
        (2, 'Uncommon'),
        (3, 'Rare'),
        (4, 'Epic'),
        (5, 'Legendary'),
    ]

    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    icon = models.CharField(max_length=100)
    rarity_threshold = models.IntegerField(choices=RARITY_CHOICES, default=1)

    def __str__(self):
        return f'{self.name} ({self.get_rarity_threshold_display()})'


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='holders')
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'badge']

    def __str__(self):
        return f'{self.user.username} — {self.badge.name}'
