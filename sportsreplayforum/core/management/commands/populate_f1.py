from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Competition, Event
from datetime import datetime
from dateutil import parser
import requests, pytz

class Command(BaseCommand):
    help = 'Populate the database with Formula 1 competitions and events'

    def handle(self, *args, **kwargs):
        # Fetch the data from the API
        response = requests.get("https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4370&s=2024")

        # Check if the request was successful
        if response.status_code != 200:
            self.stderr.write(self.style.ERROR("Failed to fetch data from the API"))
            return

        # Parse the JSON data
        data = response.json().get('events', [])
        competitions = {}

        # Step 1: Create Competitions for events ending in "Prix"
        for item in data:
            if item.get('strEvent') and item['strEvent'].endswith("Prix"):
                competition_name = item['strEvent']
                competition_date = item['dateEvent']

                # Check if competition already exists
                try:
                    Competition.objects.get(name=competition_name, date=competition_date)
                except Competition.DoesNotExist:
                    competition = Competition(
                        league=item['strLeague'],
                        name=competition_name,
                        date=datetime.strptime(competition_date, '%Y-%m-%d').date()
                    )
                    competition.save()

                    competitions[competition_name] = competition
                    date_time = parser.isoparse(item['strTimestamp']).astimezone(pytz.utc)
                    is_finished = (
                        'Finished' in item['strEvent'] or
                        item.get('intHomeScore') is not None or
                        item.get('strVideo') != ""
                    )

                    # Create a race event for the competition
                    try:
                        race_event = Event.objects.get(event_list=competition, event_type='Race', date_time=date_time)
                    except Event.DoesNotExist:
                        race_event = Event(
                            event_list=competition,
                            event_type='Race',
                            date_time=date_time,
                            idEvent=item['idEvent'],
                            video_id=item['strVideo'],
                            is_finished=is_finished
                        )
                        race_event.save()

        # Step 2: Create Events associated with each Competition
        for item in data:
            if item.get('strEvent'):
                for competition in Competition.objects.all():
                    # Check for qualifying, sprint, or sprint shootout events
                    if competition.name in item['strEvent']:
                        if 'Qualifying' in item['strEvent']:
                            event_type = 'Qualifying'
                        elif 'Sprint Shootout' in item['strEvent']:
                            event_type = 'Sprint Shootout'
                        elif 'Sprint' in item['strEvent']:
                            event_type = 'Sprint'
                        else:
                            continue  # Skip if not qualifying, sprint, or sprint shootout

                        date_time = parser.isoparse(item['strTimestamp']).astimezone(pytz.utc)
                        is_finished = (
                            'Finished' in item['strEvent'] or
                            item.get('intHomeScore') is not None or
                            item.get('strVideo') != ""
                        )

                        try:
                            event = Event.objects.get(event_list=competition, event_type=event_type, date_time=date_time)
                        except Event.DoesNotExist:
                            event = Event(
                                event_list=competition,
                                event_type=event_type,
                                date_time=date_time,
                                idEvent=item['idEvent'],
                                video_id=item['strVideo'],
                                is_finished=is_finished
                            )
                            event.save()

        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))
