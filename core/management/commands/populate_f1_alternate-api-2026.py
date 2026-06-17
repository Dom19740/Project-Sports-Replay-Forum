from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from core.models import Competition, Event
from dateutil import parser
import requests
import os
import datetime


class Command(BaseCommand):
    help = 'Populate the database with current Formula 1 competitions and events from the Jolpica F1 API'

    def handle(self, *args, **kwargs):
        api_base = os.getenv('F1_API_BASE_URL', 'https://api.jolpi.ca/ergast/f1')
        season = os.getenv('F1_SEASON', 'current')
        url = f"{api_base}/{season}/races/?limit=100"

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise CommandError(f'Failed to fetch F1 data from the Jolpica API: {e}')

        data = response.json().get('MRData', {}).get('RaceTable', {}).get('Races', [])

        if not data:
            raise CommandError('No race data returned from the Jolpica API.')

        for item in data:
            competition_name = item.get('raceName')
            competition_date = parser.isoparse(item.get('date')).date()

            competition, created = Competition.objects.get_or_create(
                name=competition_name,
                date=competition_date,
                defaults={
                    'league': 'Formula 1',
                    'banner': '',
                    'badge': '',
                }
            )

            race_date_time = self.parse_datetime(item.get('date'), item.get('time'))
            is_finished = race_date_time < timezone.now()

            race_event, created = Event.objects.get_or_create(
                event_list=competition,
                event_type='Race',
                date_time=race_date_time,
                idEvent=f"{item.get('season')}_{item.get('round')}_race",
                defaults={
                    'video_id': '',
                    'is_finished': is_finished,
                    'poster': '',
                }
            )

            if not created:
                race_event.is_finished = is_finished
                race_event.save()

            session_map = {
                'Qualifying': 'Qualifying',
                'Sprint': 'Sprint',
                'SprintQualifying': 'Sprint Shootout',
                'SprintShootout': 'Sprint Shootout',
            }

            for source_key, event_type in session_map.items():
                session_data = item.get(source_key)
                if session_data and session_data.get('date'):
                    session_date_time = self.parse_datetime(session_data.get('date'), session_data.get('time'))
                    session_event, created = Event.objects.get_or_create(
                        event_list=competition,
                        event_type=event_type,
                        date_time=session_date_time,
                        idEvent=f"{item.get('season')}_{item.get('round')}_{event_type.replace(' ', '_').lower()}",
                        defaults={
                            'video_id': '',
                            'is_finished': session_date_time < timezone.now(),
                            'poster': '',
                        }
                    )

                    if not created:
                        session_event.is_finished = session_date_time < timezone.now()
                        session_event.save()

        self.stdout.write(self.style.SUCCESS('F1 events populated and updated successfully'))

    def parse_datetime(self, date_str, time_str=None):
        if not date_str:
            raise ValueError('Missing date for F1 schedule item')

        if time_str:
            normalized_time = time_str if time_str.endswith('Z') else f"{time_str}Z"
            dt = parser.isoparse(f"{date_str}T{normalized_time}")
        else:
            dt = datetime.datetime.fromisoformat(date_str)
            dt = datetime.datetime.combine(dt.date(), datetime.time.min)
            dt = timezone.make_aware(dt)

        if dt.tzinfo is None:
            dt = timezone.make_aware(dt)

        return dt
