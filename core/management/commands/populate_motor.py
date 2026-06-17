from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models import Competition, Event
from dateutil import parser
import requests, os

class Command(BaseCommand):
    help = 'Populate the database with Formula 1 competitions and events'

    def handle(self, *args, **kwargs):

        season_ids = {
            #COMMENT OUT MOTORSPORTS HERE IF YOU WANT TO REMOVE THEM FROM THE SITE
            'MotoGP': '4407',
            #'IndyCar Series': '4373',
            #'NASCAR Cup Series': '4393',
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
                raise CommandError(f'Failed to fetch MotoGP data from the API: {e}')

            # Parse the JSON data
            data = response.json().get('events', [])

            # Step 1: Create Competitions for events ending in "Prix"
            for item in data:
                competition_name = item['strEvent']
                competition_date = parser.isoparse(item['strTimestamp']).date()

                # Check if competition already exists
                competition, created = Competition.objects.get_or_create(
                    name=competition_name,
                    date=competition_date,
                    defaults={
                        'league': item.get('strLeague', ''),
                        'banner': league_banner,
                        'badge': league_badge,
                    }
                )

                date_time = timezone.make_aware(parser.isoparse(item['strTimestamp']))
                is_finished = (
                    item['strStatus'] is not None and 'Finished' in item['strStatus'] or
                    item.get('strVideo') not in [None, ""]
                )

                # Create a race event for the competition
                race_event, created = Event.objects.get_or_create(
                    event_list=competition,
                    event_type='Race',
                    date_time=date_time,
                    idEvent=item['idEvent'],
                    defaults={
                        'video_id': item.get('strVideo', ''),  # Provide a default value if 'strVideo' is missing
                        'is_finished': is_finished,
                        'poster': item.get('strThumb', ''),  # Provide a default value if 'strThumb' is missing
                    }
                )

                if not created:
                    # If the event already exists, update the fields
                    race_event.video_id = item.get('strVideo', '')
                    race_event.is_finished = is_finished
                    race_event.save()

            self.stdout.write(self.style.SUCCESS(f"{item['strLeague']} populated successfully"))