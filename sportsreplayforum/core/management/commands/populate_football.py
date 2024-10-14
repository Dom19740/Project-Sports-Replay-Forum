from django.core.management.base import BaseCommand
from core.models import Competition, Event
from datetime import datetime
from dateutil import parser
import requests, pytz

class Command(BaseCommand):
    help = 'Populate the database with Nations League competitions and events'

    """
    4490 = UEFA Nations League
    4849 = WSL
    """

    def handle(self, *args, **kwargs):

        # Fetch the data from the API
        nl = '4490'  """Nations League"""
        wsl = '4849' """WSL"""
        pl = '4328'  """Premier League"""

        response = requests.get(f"https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id={4328}")

        # Check if the request was successful
        if response.status_code != 200:
            self.stderr.write(self.style.ERROR("Failed to fetch data from the API"))
            return

        # Parse the JSON data
        data = response.json().get('events', [])

        # Step 1: Create Competitions for events by matchday
        for item in data:
            competition_date = item['dateEvent']
            date_obj = datetime.strptime(item['dateEvent'], "%Y-%m-%d")
            competition_name = f"Matchday - {date_obj.strftime('%A %d %b')}"

            # Check if competition already exists
            try:
                competition = Competition.objects.get(name=competition_name, date=competition_date)
            except Competition.DoesNotExist:
                competition = Competition(
                    league=item['strLeague'],
                    name=competition_name,
                    date=datetime.strptime(competition_date, '%Y-%m-%d').date()
                )
                competition.save()

            is_finished = (
                'Finished' in item['strEvent'] or
                item.get('intHomeScore') is not None or
                item.get('strVideo') != ""
            )

            date_time = parser.isoparse(item['strTimestamp']).astimezone(pytz.utc)

            # Create a race event for the competition
            match_event, created = Event.objects.get_or_create(
                event_list = competition,
                event_type = item['strEvent'],
                date_time = date_time,
                idEvent = item['idEvent'],
                video_id = item['strVideo'],
                is_finished=is_finished,
            )
            match_event.save()

        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))
