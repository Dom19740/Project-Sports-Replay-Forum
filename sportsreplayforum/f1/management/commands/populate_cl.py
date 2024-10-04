from django.core.management.base import BaseCommand
from f1.models import Competition, Event
from datetime import datetime

class Command(BaseCommand):
    help = 'Populate the database with sample competition'

    def handle(self, *args, **kwargs):
        # Add a sample competition
        competition, created = Competition.objects.get_or_create(
            name="League Game",
            date="2024-10-02",
        )
        
        # Add events for the competition             
        Event.objects.get_or_create(
            event_list=competition,
            event_type="match",
            date_time=datetime(2024, 10, 2, 14, 0)
        )
        Event.objects.get_or_create(
            event_list=competition,
            event_type="match",
            date_time=datetime(2024, 9, 1, 15, 0)
        )

        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))
