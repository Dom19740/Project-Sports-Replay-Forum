from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

KEEP_USERNAMES = {'admin', 'Dominic', 'Brian'}

class Command(BaseCommand):
    help = 'Delete inactive (unverified) users older than 7 days'

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(days=7)
        to_delete = User.objects.filter(
            is_active=False,
            date_joined__lt=cutoff,
        ).exclude(username__in=KEEP_USERNAMES)

        count = to_delete.count()
        to_delete.delete()
        self.stdout.write(self.style.SUCCESS(f'Deleted {count} inactive bot accounts'))
