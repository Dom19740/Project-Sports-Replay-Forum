from django.core.management.base import BaseCommand, CommandError
from core.models import Event, Result_f1
import requests, os


class Command(BaseCommand):
    help = 'Populate event results'

    def handle(self, *args, **kwargs):
        # Fetch the event results from the API
        api_key = os.getenv('SPORTSDB_API_KEY')
        try:
            response = requests.get(f"https://www.thesportsdb.com/api/v1/json/{api_key}/eventresults.php?id={kwargs['idEvent']}")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise CommandError(f'Failed to fetch event results from the API: {e}')

        # Parse the JSON data
        data = response.json().get('results', [])

        # Populate the event results
        for item in data:
            # Find the event associated with the result
            event = Event.objects.get(id=item['idEvent'])

            # Create or update the result
            result, created = Result_f1.objects.get_or_create(
                event=event,
                position=item['intPosition'],
                driver=item['strPlayer'],
                team=item['idTeam'],
                time=item['strDetail'],
    )