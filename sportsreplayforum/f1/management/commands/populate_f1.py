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
                idEvent = event['idEvent']
                event_datetime = event['strTimestamp']
                dt = datetime.strptime(event_datetime, "%Y-%m-%dT%H:%M:%S")
                date = dt.date()

                # Check if the event text contains "Grand Prix"
                if event_text.endswith(" Prix"):
                    competition_name = event_text
                    # Check if the competition name already exists in the list
                    if competition_name not in competition_names:
                        competition_names.append(competition_name)

                        # Add a race weekend
                        competition, created = Competition.objects.get_or_create(
                            name=competition_name,
                            date=date,  
                        )

                        # Add race event
                        Event.objects.get_or_create(
                            event_list=competition,
                            event_type="race",
                            date_time=timezone.make_aware(dt)
                        )

                        # Add qualifying event
                    """if "Qualifying" in event_text:
                            Event.objects.get_or_create(
                                event_list=competition,
                                event_type="qualifying",
                                date_time=timezone.make_aware(dt),
                                idEvent = idEvent
                            )
                            """
                
        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))