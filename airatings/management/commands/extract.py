import json
from django.core.management.base import BaseCommand, CommandError
from core.models import Event
from airatings.ingest.dispatch import get_source_for_event
from airatings.stage_one import extract_signals
from airatings.models import EventSignals


class Command(BaseCommand):
    help = 'Run stage-one signal extraction for one event and save the result'

    def add_arguments(self, parser):
        parser.add_argument('event_id', type=int, help='DB primary key of the Event')
        parser.add_argument(
            '--no-save',
            action='store_true',
            help='Print result only; do not save to EventSignals',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Re-extract even if EventSignals already exists',
        )

    def handle(self, *args, **options):
        try:
            event = Event.objects.select_related('event_list').get(pk=options['event_id'])
        except Event.DoesNotExist:
            raise CommandError(f"No Event with id={options['event_id']}")

        self.stdout.write(
            f"\nEvent #{event.pk}: {event}\n"
            f"  league:  {event.event_list.league}\n"
            f"  date:    {event.date_time.date()}\n"
            f"  idEvent: {event.idEvent}\n"
        )

        # Guard: skip if already extracted unless --force
        if not options['force'] and EventSignals.objects.filter(event=event).exists():
            self.stdout.write(
                self.style.WARNING("EventSignals already exists. Use --force to re-extract.")
            )
            existing = EventSignals.objects.get(event=event)
            self.stdout.write(json.dumps(existing.signals, indent=2))
            return

        # --- Ingest -------------------------------------------------------
        source = get_source_for_event(event)
        if source is None:
            raise CommandError(f"No data source for league '{event.event_list.league}'")

        self.stdout.write("Fetching stats...")
        stats = source.get_stats(event)
        if not stats or stats == {"has_detailed_events": False}:
            raise CommandError("get_stats() returned empty — cannot extract signals without data.")

        self.stdout.write("Fetching reports...")
        reports = source.get_reports(event)
        self.stdout.write(f"  {len(reports)} report(s) found")

        # --- Stage one ----------------------------------------------------
        self.stdout.write("Calling LLM (stage one)...")
        try:
            signals = extract_signals(stats, reports)
        except RuntimeError as exc:
            raise CommandError(str(exc))

        # --- Output -------------------------------------------------------
        self.stdout.write(self.style.SUCCESS("\n--- Signals ---"))
        self.stdout.write(json.dumps(signals, indent=2))

        if not options['no_save']:
            obj, created = EventSignals.objects.update_or_create(
                event=event,
                defaults={"signals": signals},
            )
            verb = "Created" if created else "Updated"
            self.stdout.write(self.style.SUCCESS(f"\n{verb} EventSignals pk={obj.pk}"))
