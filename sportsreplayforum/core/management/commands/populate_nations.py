from django.core.management.base import BaseCommand
from core.models import Competition, Event
from datetime import datetime
from dateutil import parser
import requests

class Command(BaseCommand):
    help = 'Populate the database with Nations League competitions and events'

    def handle(self, *args, **kwargs):
        # Fetch the data from the API
        response = requests.get("https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4490")

        # Check if the request was successful
        if response.status_code != 200:
            self.stderr.write(self.style.ERROR("Failed to fetch data from the API"))
            return

        # Parse the JSON data
        data = response.json().get('events', [])
        competitions = {}

        # Step 1: Create Competitions for events ending in "Prix"
        for item in data:
            competition_name = item['strEvent']
            competition_date = item['dateEvent']

            # Check if competition already exists
            if competition_name not in competitions:
                competition = Competition(
                    league = item['strLeague'],
                    name = competition_name,
                    date = datetime.strptime(competition_date, '%Y-%m-%d').date()
                )
                competition.save()
                competitions[competition_name] = competition

                # Create a race event for the competition
                race_event = Event(
                    event_list = competition,
                    event_type = 'Match',
                    date_time = parser.isoparse(item['strTimestamp']),
                    idEvent = item['idEvent'],
                    video_id = item['strVideo'],
                )
                race_event.save()

        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))
