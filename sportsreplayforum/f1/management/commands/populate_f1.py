from django.core.management.base import BaseCommand
from f1.models import Competition, Event
from datetime import datetime
from django.utils import timezone

import requests
import json


class Command(BaseCommand):
    help = 'Populate the database with sample races and events'

    def handle(self, *args, **kwargs):

        response = requests.get(f"https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4370&s=2024")


        # Check if the response is valid
        if response.status_code == 200:
            # Convert the response to JSON format
            data = response.json()
            
            # Assuming the API response contains a list of events
            events = data['events']
            
            competition_names = []

            for event in events:
                # Extract the text in 'strEvent'
                event_text = event['strEvent']
                
                # Check if the event text contains "Grand Prix"
                if "Grand Prix" in event_text:
                    # Split the text at the word 'Prix' and take the first part
                    competition_name = event_text.split('Prix')[0] + 'Prix'
                    
                    # Check if the competition name already exists in the list
                    if competition_name not in competition_names:
                        competition_names.append(competition_name)

                    # Add a sample race
                    competition, created = Competition.objects.get_or_create(
                        name = competition_name,
                        date = "1974-06-10",
                        idEvent = "1234567"
                    )
                    
                    # Add events for the race             
                    Event.objects.get_or_create(
                        event_list=competition,
                        event_type="qualifying",
                        date_time=timezone.make_aware(datetime(2024, 8, 30, 14, 0)),
                    )
                    Event.objects.get_or_create(
                        event_list=competition,
                        event_type="race",
                        date_time=timezone.make_aware(datetime(2024, 9, 1, 15, 0))
                    )
                    if "Sprint" in event_text:
                        Event.objects.get_or_create(
                            event_list=competition,
                            event_type="sprint",
                            date_time=timezone.make_aware(datetime(2024, 9, 1, 15, 0))
                        )
                    if "Shootout" in event_text:
                        Event.objects.get_or_create(
                            event_list=competition,
                            event_type="sprint shootout",
                            date_time=timezone.make_aware(datetime(2024, 9, 1, 15, 0))
                        )


        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))