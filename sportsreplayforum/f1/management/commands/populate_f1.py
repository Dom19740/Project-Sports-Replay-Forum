from django.core.management.base import BaseCommand
from f1.models import Competition, Event
from datetime import datetime
from django.utils import timezone

import requests
import json
























class Command(BaseCommand):
    help = 'Populate the database with sample races and events'

    def handle(self, *args, **kwargs):
        # Add a sample race
        competition, created = Competition.objects.get_or_create(
            name="German Grand Prix",
            date="2024-09-01",
            round="16"
        )
        
        # Add events for the race             
        Event.objects.get_or_create(
            event_list=competition,
            event_type="qualifying",
            date_time=timezone.make_aware(datetime(2024, 8, 30, 14, 0))
        )
        Event.objects.get_or_create(
            event_list=competition,
            event_type="race",
            date_time=timezone.make_aware(datetime(2024, 9, 1, 15, 0))
        )

        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))