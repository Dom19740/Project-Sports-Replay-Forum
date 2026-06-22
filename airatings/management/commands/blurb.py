from django.core.management.base import BaseCommand, CommandError
from core.models import Event
from airatings.models import EventSignals
from airatings.verdict import map_to_verdict
from airatings.stage_two import write_blurb


class Command(BaseCommand):
    help = 'Generate a spoiler-free blurb for one event (stage two)'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, help='DB primary key of the Event')

    def handle(self, *args, **options):
        try:
            event = Event.objects.select_related('event_list').get(pk=options['event_id'])
        except Event.DoesNotExist:
            raise CommandError(f"No Event with id={options['event_id']}")

        try:
            es = EventSignals.objects.get(event=event)
        except EventSignals.DoesNotExist:
            raise CommandError(
                f"No EventSignals for event #{event.pk}. Run 'extract {event.pk}' first."
            )

        verdict = map_to_verdict(es.signals)

        self.stdout.write(
            f"\nEvent #{event.pk}: {event}\n"
            f"  Verdict: {verdict['stars']}★  {verdict['verdict']}\n"
            f"  Rationale: {verdict['rationale_internal']}\n"
        )

        self.stdout.write("Calling LLM (stage two)...")
        try:
            blurb = write_blurb(es.signals, verdict)
        except RuntimeError as exc:
            raise CommandError(str(exc))

        self.stdout.write(self.style.SUCCESS(f"\nBlurb:\n  {blurb}\n"))
