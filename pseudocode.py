from django.core.management.base import BaseCommand
from f1.models import Competition, Event
from datetime import datetime
from dateutil import parser
from django.utils import timezone
from datetime import datetime

import requests
import json


class Command(BaseCommand):
    help = 'Populate the database with sample races and events'

    def handle(self, *args, **kwargs):

        # Assuming you have the JSON data in a variable called `data`
        response = requests.get(f"https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4370&s=2024")
        data = response.json()

        # Step 1: Create Competitions for events ending in "Prix"
        competitions = {}
        for item in data:
            if item['strEvent'] and item['strEvent'].endswith("Prix"):
                competition_name = item['strEvent']
                competition_date = item['dateEvent']
                
                # Check if competition already exists
                if competition_name not in competitions:
                    competition = Competition(name=competition_name, date=datetime.strptime(competition_date, '%Y-%m-%d').date())
                    competition.save()
                    competitions[competition_name] = competition

        # Step 2: Create Events associated with each Competition
        for item in data:
            if item['strEvent']:
                for competition_name, competition in competitions.items():
                    # Check for qualifying, sprint, or sprint shootout events
                    if competition_name in item['strEvent']:
                        if 'Qualifying' in item['strEvent']:
                            event_type = 'Qualifying'
                        elif 'Sprint' in item['strEvent']:
                            event_type = 'Sprint'
                        elif 'Sprint Shootout' in item['strEvent']:
                            event_type = 'Sprint Shootout'
                        else:
                            continue  # Skip if not qualifying, sprint, or sprint shootout

                        event = Event(
                            event_list=competition,
                            event_type=event_type,
                            date_time=datetime.strptime(item['strTimestamp'], '%Y-%m-%dT%H:%M:%S'),
                            idEvent=item['idEvent']
                        )
                        event.save()
                
        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))


        