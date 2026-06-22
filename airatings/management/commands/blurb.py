from django.core.management.base import BaseCommand, CommandError
from core.models import Event
from airatings.models import EventSignals
from airatings.verdict import map_to_verdict
from airatings.guard import run_with_guard


class Command(BaseCommand):
    help = 'Generate a spoiler-free blurb for one event (stage two + guard)'

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
            f"  {verdict['rationale_internal']}\n"
        )

        self.stdout.write("Generating blurb (stage two + guard)...")
        blurb, is_safe, reasons = run_with_guard(es.signals, verdict, event)

        if is_safe:
            self.stdout.write(self.style.SUCCESS(f"\nBlurb [SAFE]:\n  {blurb}\n"))
        else:
            self.stdout.write(self.style.ERROR("\n⚠  MANUAL REVIEW REQUIRED"))
            self.stdout.write(f"  Reasons: {'; '.join(reasons)}")
            self.stdout.write(f"\nBlurb [UNSAFE — do not publish]:\n  {blurb}\n")
