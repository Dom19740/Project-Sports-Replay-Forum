from django.core.management.base import BaseCommand
from core.models import Competition, Event
from datetime import datetime
from dateutil import parser
import requests

class Command(BaseCommand):
    help = 'Populate the database with Nations League competitions and events'

    """
    Nations League = eventsseason.php?id=4490
    WSL = eventsseason.php?id=4849
    """

    def handle(self, *args, **kwargs):
        # Fetch the data from the API
        response = requests.get("https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4849")

        # Check if the request was successful
        if response.status_code != 200:
            self.stderr.write(self.style.ERROR("Failed to fetch data from the API"))
            return

        # Parse the JSON data
        data = response.json().get('events', [])
        competitions = {}

        # Step 1: Create Competitions for events ending in "Prix"
        for item in data:
            competition_date = item['dateEvent']

            # parse the strTimestamp field into a datetime object
            dt = datetime.strptime(competition_date, "%Y-%m-%d")

            # Check if competition already exists
            if competition_date not in competitions:
                    competition = Competition(
                        league = item['strLeague'],
                        name = dt.strftime("%A %d %B"),
                        date = datetime.strptime(competition_date, '%Y-%m-%d').date()
                    )
                    competition.save()
                    competitions[competition_date] = competition

            # Create a race event for the competition
            match_event = Event(
                event_list = competition,
                event_type = item['strEvent'],
                date_time = parser.isoparse(item['strTimestamp']),
                idEvent = item['idEvent'],
                video_id = item['strVideo'],
            )
            match_event.save()

        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))
