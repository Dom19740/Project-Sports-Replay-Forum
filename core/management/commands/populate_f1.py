from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models import Competition, Event
from dateutil import parser
from datetime import timedelta
import requests, os

class Command(BaseCommand):
    help = 'Populate the database with Formula 1 competitions and events'

    def handle(self, *args, **kwargs):
        api_key = os.getenv('SPORTSDB_API_KEY')

        # Fetch league banner and badge from league endpoint
        try:
            league_response = requests.get(f"https://www.thesportsdb.com/api/v1/json/{api_key}/lookupleague.php?id=4370")
            league_response.raise_for_status()
            league_info = league_response.json().get('leagues', [{}])[0]
            league_banner = league_info.get('strBanner', '')
            league_badge = league_info.get('strBadge', '')
        except (requests.exceptions.RequestException, IndexError):
            league_banner = ''
            league_badge = ''

        try:
            response = requests.get(f"https://www.thesportsdb.com/api/v1/json/{api_key}/eventsseason.php?id=4370&s=2026")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise CommandError(f'Failed to fetch F1 data from the API: {e}')

        # Parse the JSON data
        data = response.json().get('events', [])

        # Delete events and competitions over 2 weeks old
        two_weeks_ago = timezone.now() - timedelta(weeks=2)
        Event.objects.filter(date_time__lt=two_weeks_ago).delete()
        Competition.objects.filter(events__isnull=True).delete()

        # Step 1: Create or update Competitions for events ending in "Prix"
        for item in data:
            if item.get('strEvent') and item['strEvent'].endswith("Prix"):
                competition_name = item['strEvent']
                competition_date = parser.isoparse(item['strTimestamp']).date()

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

                # Check if competition already exists, or create a new one
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
                    'Finished' in item['strStatus'] or
                    item.get('strVideo') != ""
                )

                # Create or update the race event for the competition
                race_event, created = Event.objects.get_or_create(
                    event_list=competition,
                    event_type='Race',
                    date_time=date_time,
                    idEvent=item['idEvent'],
                    defaults={
                        'video_id': item['strVideo'],
                        'is_finished': is_finished,
                        'poster': item['strThumb'],
                    }
                )

                if not created:
                    # If the event already exists, update the fields
                    race_event.video_id = item['strVideo']
                    race_event.is_finished = is_finished
                    race_event.save()

        # Step 2: Create or update Events associated with each Competition (e.g., Qualifying, Sprint)
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

                        date_time = timezone.make_aware(parser.isoparse(item['strTimestamp']))
                        is_finished = (
                            'Finished' in item['strStatus'] or
                            item.get('strVideo') != ""
                        )

                        # Create or update the event
                        event, created = Event.objects.get_or_create(
                            event_list=competition,
                            event_type=event_type,
                            date_time=date_time,
                            idEvent=item['idEvent'],
                            defaults={
                                'video_id': item['strVideo'],
                                'is_finished': is_finished,
                                'poster': item['strThumb'],
                            }
                        )

                        if not created:
                            # If the event already exists, update the fields
                            event.video_id = item['strVideo']
                            event.is_finished = is_finished
                            event.save()

        self.stdout.write(self.style.SUCCESS("F1 events populated and updated successfully"))
