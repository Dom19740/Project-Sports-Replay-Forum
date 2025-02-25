from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models import Competition, Event
from datetime import datetime, timedelta
from dateutil import parser
import requests, os

class Command(BaseCommand):
    help = 'Populate the database with Nations League competitions and events'

    def handle(self, *args, **kwargs):
        season_ids = {
            'UEFA Champions League': '4480',
            'Premier League': '4328',
            #'NFL': '4391',
            #'NBA': '4387',
            #'NHL': '4380',
        }
        for season_name, season_id in season_ids.items():
            # Fetch the data from the API
            api_key = os.getenv('SPORTSDB_API_KEY')
            try:
                response = requests.get(f"https://www.thesportsdb.com/api/v1/json/{api_key}/eventsseason.php?id={season_id}")
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise CommandError(f'Error fetching data for {season_name}: {e}')

            # Parse the JSON data
            data = response.json().get('events', [])

            # Define the date range
            start_date = datetime.now() - timedelta(days=30)  # 1 month ago
            end_date = datetime.now() + timedelta(days=30)  # 1 month from now

            filtered_data = [item for item in data if start_date <= parser.isoparse(item['strTimestamp']) <= end_date]

            # Delete competitions that are over 4 months old
            four_months_ago = datetime.now() - timedelta(days=120)
            Event.objects.filter(event_list__date__lt=four_months_ago).delete()
            Competition.objects.filter(date__lt=four_months_ago).delete()

            # Step 1: Create Competitions for events by matchday
            for item in filtered_data:
                date_obj = datetime.strptime(item['dateEvent'], "%Y-%m-%d")
                competition_name = date_obj.strftime('%a %d %b')
                competition_date = parser.isoparse(item['strTimestamp']).date()

                # Check if competition already exists
                competition, created = Competition.objects.get_or_create(
                    league=item['strLeague'],
                    name=competition_name,
                    date=competition_date,
                    defaults={
                        'banner': item['strLeagueBadge'],
                        'badge': item['strLeagueBadge'],
                    }
                )

                date_time = timezone.make_aware(parser.isoparse(item['strTimestamp']))
                is_finished = (
                    item.get('strStatus', '') == 'Match Finished'
                )
                
                # Create a match event for the competition
                match_event, created = Event.objects.get_or_create(
                    event_list = competition,
                    event_type = item['strEvent'],
                    date_time = date_time,
                    idEvent = item['idEvent'],
                    defaults={
                        'video_id': item['strVideo'],
                        'is_finished': is_finished,
                        'poster': item['strThumb'],
                    }
                )

                if not created:
                    # If the event already exists, update the fields
                    match_event.video_id = item['strVideo']
                    match_event.is_finished = is_finished
                    match_event.save()

            self.stdout.write(self.style.SUCCESS(f"{item['strLeague']} populated successfully"))
 