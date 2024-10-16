from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models import Competition, Event
from datetime import datetime
from dateutil import parser
import requests

class Command(BaseCommand):
    help = 'Populate the database with Nations League competitions and events'

    """
    4490 = UEFA Nations League
    4480 = UEFA Champions League
    4328 = Premier League
    4429 = World Cup
    """

    def handle(self, *args, **kwargs):

        # Fetch the data from the API
        try:
            response = requests.get(f"https://www.thesportsdb.com/api/v1/json/449702/eventsseason.php?id=4480")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise CommandError(f'Failed to fetch data from the API: {e}')

        # Parse the JSON data
        data = response.json().get('events', [])

        # Step 1: Create Competitions for events by matchday
        for item in data:

            date_obj = datetime.strptime(item['dateEvent'], "%Y-%m-%d")
            competition_name = date_obj.strftime('%A %d %b')
            competition_date = parser.isoparse(item['strTimestamp']).date()

            # Check if competition already exists
            competition, created = Competition.objects.get_or_create(
                league=item['strLeague'],
                name=competition_name,
                date=competition_date,
            )

            if created:
                competition.save()

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
                }
            )

            if not created:
                # Update the fields if the event already exists
                Event.objects.filter(pk=match_event.pk).update(
                    video_id=item['strVideo'],
                    is_finished=is_finished,
                )
            if created:
                match_event.save()

        self.stdout.write(self.style.SUCCESS(f"{item['strLeague']} populated successfully"))
 