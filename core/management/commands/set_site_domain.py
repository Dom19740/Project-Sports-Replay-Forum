from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Set the site domain and name'

    def handle(self, *args, **kwargs):
        if settings.DJANGO_ENV == 'local':
            Site.objects.update_or_create(
                id=1,
                defaults={
                    'domain': '127.0.0.1:5000',
                    'name': 'Local Site'
                }
            )
        else:
            Site.objects.update_or_create(
                id=1,
                defaults={
                    'domain': 'shouldiwatchsports.com',
                    'name': 'Should I Watch Sports'
                }
            )
            Site.objects.update_or_create(
                id=2,
                defaults={
                    'domain': 'www.shouldiwatchsports.com',
                    'name': 'Should I Watch Sports'
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully set site domain and name'))