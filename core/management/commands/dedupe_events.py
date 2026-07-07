from collections import defaultdict

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Event


def dedupe_events(stdout=None):
    """
    Find Events that share the same idEvent. This happens when a source
    reschedule/postponement changes date_time and an importer's get_or_create
    (previously keyed on date_time as well as idEvent) can't find the
    existing row, so it creates a second one instead of updating in place.

    Keeps the most recently created row per idEvent (it reflects the latest
    data pulled from the source) and removes older duplicates — but only if
    they haven't gone live yet. An event that's already happened may have
    real ratings/comments attached, so those are left alone and flagged.

    Returns (removed_count, skipped_count).
    """
    def _log(msg):
        if stdout:
            stdout.write(msg)

    groups = defaultdict(list)
    for event in Event.objects.exclude(idEvent='').order_by('id'):
        groups[event.idEvent].append(event)

    removed = 0
    skipped = 0
    for id_event, events in groups.items():
        if len(events) < 2:
            continue

        *older, newest = events
        for stale in older:
            has_gone_live = stale.is_finished or stale.date_time <= timezone.now()
            if has_gone_live:
                _log(
                    f'Skipping duplicate idEvent={id_event}: event {stale.id} '
                    f'("{stale}") has already gone live — left in place.'
                )
                skipped += 1
                continue

            _log(
                f'Removing stale duplicate idEvent={id_event}: event {stale.id} '
                f'("{stale}") — kept event {newest.id} ("{newest}").'
            )
            stale.delete()
            removed += 1

    return removed, skipped


class Command(BaseCommand):
    help = (
        "Find Events that share the same idEvent (duplicates created when a "
        "postponement/reschedule changed date_time before an event's next "
        "import run) and remove the older row, as long as it hasn't gone "
        "live yet."
    )

    def handle(self, *args, **kwargs):
        removed, skipped = dedupe_events(stdout=self.stdout)
        self.stdout.write(self.style.SUCCESS(
            f'Done — removed {removed} stale duplicate event(s), skipped {skipped} (already live).'
        ))
