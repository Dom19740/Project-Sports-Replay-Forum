from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from core.models import Rating
from gamify.badges import check_badges
from gamify.models import XPEvent


class Command(BaseCommand):
    help = 'Backfill rating.voters from XP events, then award any pending badges.'

    def handle(self, *args, **options):
        self._backfill_voters()
        self._award_badges()

    def _backfill_voters(self):
        """
        rating.voters was not populated by the vote view before this fix.
        Reconstruct it from event_rated XPEvents so badge conditions work.
        """
        qs = (
            XPEvent.objects
            .filter(action_type='event_rated', related_event__isnull=False)
            .select_related('user', 'related_event')
        )
        added = 0
        for xp in qs:
            try:
                rating = xp.related_event.rating
            except Rating.DoesNotExist:
                continue
            if not rating.voters.filter(pk=xp.user_id).exists():
                rating.voters.add(xp.user)
                added += 1

        if added:
            self.stdout.write(f'Backfilled {added} voter relationship(s).')

    def _award_badges(self):
        User = get_user_model()
        total_awarded = 0

        for user in User.objects.filter(is_active=True):
            newly = check_badges(user)
            for badge in newly:
                self.stdout.write(f'  {user.username}: awarded "{badge.name}"')
                total_awarded += 1

        if total_awarded:
            self.stdout.write(self.style.SUCCESS(f'Done — {total_awarded} badge(s) awarded.'))
        else:
            self.stdout.write('No new badges to award.')
