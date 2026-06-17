from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Competition, Event
from datetime import timedelta


class Command(BaseCommand):
    help = 'Remove events and competitions older than 2 weeks'

    def handle(self, *args, **kwargs):
        cutoff = timezone.now() - timedelta(weeks=2)

        deleted_events, _ = Event.objects.filter(date_time__lt=cutoff).delete()
        deleted_comps, _ = Competition.objects.filter(events__isnull=True).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Deleted {deleted_events} events and {deleted_comps} empty competitions'
        ))
