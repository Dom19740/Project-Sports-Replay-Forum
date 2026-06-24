from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models import Competition, Event
from datetime import datetime, timedelta
from dateutil import parser
import requests, os

class Command(BaseCommand):
    help = 'Populate the database with US competitions and events'

    def handle(self, *args, **kwargs):
        season_ids = {
            #'NFL': '4391',
            #'NBA': '4387',
            #'NHL': '4380',
        }
        api_key = os.getenv('SPORTSDB_API_KEY')
        for season_name, season_id in season_ids.items():
            # Fetch league banner and badge from league endpoint
            try:
                league_response = requests.get(f"https://www.thesportsdb.com/api/v1/json/{api_key}/lookupleague.php?id={season_id}")
                league_response.raise_for_status()
                league_info = league_response.json().get('leagues', [{}])[0]
                league_banner = league_info.get('strBanner', '')
                league_badge = league_info.get('strBadge', '')
            except (requests.exceptions.RequestException, IndexError):
                league_banner = ''
                league_badge = ''

            # Fetch the data from the API
            try:
                response = requests.get(f"https://www.thesportsdb.com/api/v1/json/{api_key}/eventsseason.php?id={season_id}")
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                raise CommandError(f'Error fetching data for {season_name}: {e}')

            # Parse the JSON data
            data = response.json().get('events', [])

            # Define the date range
            now = timezone.now()
            start_date = now - timedelta(days=30)  # 1 month ago
            end_date = now + timedelta(days=30)  # 1 month from now

            def _aware(ts):
                dt = parser.isoparse(ts)
                return timezone.make_aware(dt) if dt.tzinfo is None else dt

            filtered_data = [item for item in data if start_date <= _aware(item['strTimestamp']) <= end_date]

            # Delete competitions that are over 4 months old
            two_weeks_ago = now - timedelta(weeks=2)
            Event.objects.filter(date_time__lt=two_weeks_ago).delete()
            Competition.objects.filter(events__isnull=True).delete()

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
                        'banner': league_banner,
                        'badge': league_badge,
                    }
                )

                date_time = timezone.make_aware(parser.isoparse(item['strTimestamp']))
                _status = item.get('strStatus', '')
                is_finished = _status in {'FT', 'AET', 'PEN', 'AOT', 'FT_PEN', 'Finished', 'Match Finished'}
                
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
 