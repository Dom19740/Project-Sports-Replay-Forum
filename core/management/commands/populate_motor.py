from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models import Competition, Event
from dateutil import parser
import requests, os

class Command(BaseCommand):
    help = 'Populate the database with motorsport competitions and events'

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
                raise CommandError(f'Failed to fetch {season_name} data from the API: {e}')

            # Parse the JSON data
            data = response.json().get('events', [])

            # Step 1: Create Competitions for GP events and their Race sub-event
            for item in data:
                event_name = item.get('strEvent', '').strip()
                if not event_name.endswith(' GP') and not event_name.endswith('  GP'):
                    continue

                competition_name = event_name

                # Fetch event-specific banner via individual event lookup
                event_banner = league_banner
                try:
                    event_response = requests.get(
                        f"https://www.thesportsdb.com/api/v1/json/{api_key}/lookupevent.php?id={item['idEvent']}"
                    )
                    event_response.raise_for_status()
                    event_detail = event_response.json().get('events', [{}])[0]
                    event_banner = event_detail.get('strBanner', '') or league_banner
                except (requests.exceptions.RequestException, IndexError):
                    pass

                competition_date = parser.isoparse(item['strTimestamp']).date()
                competition, created = Competition.objects.get_or_create(
                    name=competition_name,
                    date=competition_date,
                    defaults={
                        'league': item.get('strLeague', ''),
                        'banner': event_banner,
                        'badge': league_badge,
                    }
                )

                if not created and event_banner:
                    competition.banner = event_banner
                    competition.save()

                date_time = timezone.make_aware(parser.isoparse(item['strTimestamp']))
                is_finished = (
                    item.get('strStatus') is not None and 'Finished' in item.get('strStatus', '') or
                    item.get('strVideo') not in [None, '']
                )

                race_event, created = Event.objects.get_or_create(
                    event_list=competition,
                    event_type='Race',
                    date_time=date_time,
                    idEvent=item['idEvent'],
                    defaults={
                        'video_id': item.get('strVideo', ''),
                        'is_finished': is_finished,
                        'poster': item.get('strThumb', ''),
                    }
                )

                if not created:
                    race_event.video_id = item.get('strVideo', '')
                    race_event.is_finished = is_finished
                    race_event.save()

            # Step 2: Create sub-events (Sprint Race, Qualifying) under each Competition
            for item in data:
                event_name = item.get('strEvent', '').strip()
                if not event_name:
                    continue

                for competition in Competition.objects.filter(league=season_name):
                    location = competition.name.replace(' GP', '').strip()
                    if not event_name.startswith(location + ' '):
                        continue

                    if 'Sprint Race' in event_name:
                        event_type = 'Sprint Race'
                    elif 'Qualifying 1' in event_name:
                        event_type = 'Qualifying 1'
                    elif 'Qualifying 2' in event_name:
                        event_type = 'Qualifying 2'
                    else:
                        continue

                    date_time = timezone.make_aware(parser.isoparse(item['strTimestamp']))
                    is_finished = (
                        item.get('strStatus') is not None and 'Finished' in item.get('strStatus', '') or
                        item.get('strVideo') not in [None, '']
                    )

                    event, created = Event.objects.get_or_create(
                        event_list=competition,
                        event_type=event_type,
                        date_time=date_time,
                        idEvent=item['idEvent'],
                        defaults={
                            'video_id': item.get('strVideo', ''),
                            'is_finished': is_finished,
                            'poster': item.get('strThumb', ''),
                        }
                    )

                    if not created:
                        event.video_id = item.get('strVideo', '')
                        event.is_finished = is_finished
                        event.save()

            self.stdout.write(self.style.SUCCESS(f"{season_name} populated successfully"))
