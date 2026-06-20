from django.core.management.base import BaseCommand
from airatings.llm_client import complete


class Command(BaseCommand):
    help = 'Send a test prompt through the LLM wrapper and print the result'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Test json_mode (requests raw JSON back)',
        )

    def handle(self, *args, **options):
        if options['json']:
            system = 'You rate sports events.'
            user = 'Return a JSON object with keys "rating" (integer 0-100) and "review" (one sentence) for a fictional F1 race.'
            self.stdout.write('Testing json_mode=True ...\n')
        else:
            system = 'You are a helpful assistant.'
            user = 'Say "LLM wrapper is working." and nothing else.'
            self.stdout.write('Testing plain text mode ...\n')

        result = complete(system, user, json_mode=options['json'])
        self.stdout.write(self.style.SUCCESS(result))
