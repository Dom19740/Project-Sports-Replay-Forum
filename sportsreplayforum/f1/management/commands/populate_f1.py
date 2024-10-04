from django.core.management.base import BaseCommand
from f1.models import Competition, Event
from datetime import datetime
import requests
import json

class Command(BaseCommand):
    help = 'Populate the database with Formula 1 competitions and events'

    def handle(self, *args, **kwargs):
        url = "https://www.thesportsdb.com/api/v1/json/3/eventsseason.php?id=4370&s=2024"
        response = requests.get(url)
        data = response.json()

        competitions = {}
        for entry in data['events']:
            if 'Prix' in entry['strEvent']:
                competition_name = entry['strEvent'].split('Prix')[0] + ' Prix'
                if competition_name not in competitions:
                    competition_date = None
                    for e in data['events']:
                        if competition_name in e['strEvent']:
                            if competition_date is None or e['dateEvent'] > competition_date:
                                competition_date = e['dateEvent']
                    if competition_date is not None:  # Add this check
                        competitions[competition_name] = {
                            'date': datetime.strptime(competition_date, '%Y-%m-%d'),
                            'round': entry['intRound']
                        }
                    else:
                        print(f"No date found for competition {competition_name}")

        for competition_name, competition_data in competitions.items():
            competition, created = Competition.objects.get_or_create(
                name=competition_name,
                date=competition_data['date'],
                round=competition_data['round']
            )

            # Create events for the competition
            for entry in data['events']:
                if entry['strEvent'].startswith(competition_name):
                    # Race event
                    Event.objects.get_or_create(
                        event_list=competition,
                        event_type='race',
                        date_time=competition_data['date']
                    )

                elif 'Qualifying' in entry['strEvent'] and competition_name in entry['strEvent']:
                    # Qualifying event
                    Event.objects.get_or_create(
                        event_list=competition,
                        event_type='qualifying',
                        date_time=datetime.strptime(entry['dateEvent'], '%Y-%m-%d')
                    )

                elif 'Sprint' in entry['strEvent'] and competition_name in entry['strEvent']:
                    # Sprint event
                    Event.objects.get_or_create(
                        event_list=competition,
                        event_type='sprint',
                        date_time=datetime.strptime(entry['dateEvent'], '%Y-%m-%d')
                    )

                elif 'Sprint Shootout' in entry['strEvent'] and competition_name in entry['strEvent']:
                    # Sprint shootout event
                    Event.objects.get_or_create(
                        event_list=competition,
                        event_type='sprint shootout',
                        date_time=datetime.strptime(entry['dateEvent'], '%Y-%m-%d')
                    )

        self.stdout.write(self.style.SUCCESS("Competitions and events populated successfully"))