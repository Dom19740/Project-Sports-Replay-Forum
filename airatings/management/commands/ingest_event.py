import json
from django.core.management.base import BaseCommand, CommandError
from core.models import Event
from airatings.ingest.dispatch import get_source_for_event


class Command(BaseCommand):
    help = 'Fetch and print stats for one event (eyeball data quality before running the pipeline)'

    def add_arguments(self, parser):
        parser.add_argument(
            'event_id',
            type=int,
            help='DB primary key of the Event to ingest',
        )
        parser.add_argument(
            '--show-reports',
            action='store_true',
            help='Also call get_reports() — Phase 2 sources',
        )

    def handle(self, *args, **options):
        try:
            event = Event.objects.select_related('event_list').get(pk=options['event_id'])
        except Event.DoesNotExist:
            raise CommandError(f"No Event with id={options['event_id']}")

        self.stdout.write(
            f"\nEvent #{event.pk}: {event}\n"
            f"  league:    {event.event_list.league}\n"
            f"  type:      {event.event_type}\n"
            f"  date:      {event.date_time.date()}\n"
            f"  idEvent:   {event.idEvent}\n"
            f"  finished:  {event.is_finished}\n"
        )

        source = get_source_for_event(event)
        if source is None:
            self.stdout.write(
                self.style.WARNING(
                    f"No data source registered for league '{event.event_list.league}'"
                )
            )
            return

        self.stdout.write(f"Source: {source.__class__.__name__}\n")
        self.stdout.write("Fetching stats...\n")

        stats = source.get_stats(event)

        if not stats or stats == {"has_detailed_events": False}:
            self.stdout.write(
                self.style.WARNING(
                    "get_stats() returned empty — check WARNING logs above for details."
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS("\n--- Stats ---"))
            self.stdout.write(json.dumps(stats, indent=2, default=str))

        if options['show_reports']:
            reports = source.get_reports(event)
            self.stdout.write(f"\n--- Reports ({len(reports)}) ---")
            for r in reports:
                self.stdout.write(f"  {r}")
