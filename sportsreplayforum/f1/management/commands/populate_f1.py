from django.core.management.base import BaseCommand
from f1.models import Race, Event
from datetime import datetime

class Command(BaseCommand):
    help = 'Populate the database with sample races and events'

    def handle(self, *args, **kwargs):
        # Add a sample race
        race, created = Race.objects.get_or_create(
            name="Azerbaijan Grand Prix",
            date="2024-09-15"
        )
        
        # Add events for the race
        Event.objects.get_or_create(
            race_weekend=race,
            event_type="practice",
            date_time=datetime(2024, 9, 13, 10, 0)
        )
        Event.objects.get_or_create(
            race_weekend=race,
            event_type="practice",
            date_time=datetime(2024, 9, 13, 12, 0)
        )
        Event.objects.get_or_create(
            race_weekend=race,
            event_type="practice",
            date_time=datetime(2024, 9, 14, 10, 0)
        )                
        Event.objects.get_or_create(
            race_weekend=race,
            event_type="qualifying",
            date_time=datetime(2024, 9, 14, 14, 0)
        )
        Event.objects.get_or_create(
            race_weekend=race,
            event_type="race",
            date_time=datetime(2024, 9, 15, 15, 0)
        )

        self.stdout.write(self.style.SUCCESS("Races and events populated successfully"))
