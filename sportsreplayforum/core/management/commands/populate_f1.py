from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models import Competition, Event
from dateutil import parser
import requests

class Command(BaseCommand):
    help = 'Populate the database with Formula 1 competitions and events'

    def handle(self, *args, **kwargs):
        # Fetch the data from the API
        try:
            response = requests.get("https://www.thesportsdb.com/api/v2/json/449702/eventsseason.php?id=4370&s=2024")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise CommandError(f'Failed to fetch data from the API: {e}')

        # Parse the JSON data
        data = response.json().get('events', [])

        # Step 1: Create Competitions for events ending in "Prix"
        for item in data:

            if item.get('strEvent') and item['strEvent'].endswith("Prix"):
                competition_name = item['strEvent']
                competition_date = parser.isoparse(item['strTimestamp']).date()

                # Check if competition already exists
                competition, created = Competition.objects.get_or_create(
                    name=competition_name,
                    date=competition_date,
                    defaults={
                        'league': item['strLeague'],
                    }
                )

                if created:
                    competition.save()

                date_time = timezone.make_aware(parser.isoparse(item['strTimestamp']))
                is_finished = (
                    'Finished' in item['strStatus'] or
                    item.get('strVideo') != ""
                )

                # Create a race event for the competition
                race_event, created = Event.objects.get_or_create(
                    event_list=competition,
                    event_type='Race',
                    date_time=date_time,
                    idEvent=item['idEvent'],
                    defaults={
                        'video_id': item['strVideo'],
                        'is_finished': is_finished,
                    }
                )

                if not created:
                    # Update the fields if the event already exists
                    Event.objects.filter(pk=race_event.pk).update(
                        video_id=item['strVideo'],
                        is_finished=is_finished,
                    )

                if created:
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

                        date_time = timezone.make_aware(parser.isoparse(item['strTimestamp']))
                        is_finished = (
                            'Finished' in item['strStatus'] or
                            item.get('strVideo') != ""
                        )

                        event, created = Event.objects.get_or_create(
                            event_list=competition,
                            event_type=event_type,
                            date_time=date_time,
                            idEvent=item['idEvent'],
                            defaults={
                                'video_id': item['strVideo'],
                                'is_finished': is_finished,
                            }
                        )

                        if not created:
                            # Update the fields if the event already exists
                            Event.objects.filter(pk=race_event.pk).update(
                                video_id=item['strVideo'],
                                is_finished=is_finished,
                            )

                        if created:
                            event.save()

        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))
