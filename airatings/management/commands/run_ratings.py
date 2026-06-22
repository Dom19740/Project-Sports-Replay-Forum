import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Event
from airatings.models import AIRating
from airatings.pipeline import PipelineError, is_event_finished, run_pipeline

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = (
        "Find events that have finished (strStatus = FT/AET/PEN) and run the "
        "AI rating pipeline on each unrated one. Idempotent — safe to re-run."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--event-id",
            type=int,
            default=None,
            help="Process a single event by PK (for debugging). Ignores finished check.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Check which events would be processed without calling any LLM.",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Re-process events that already have a pending or flagged AIRating.",
        )

    def handle(self, *args, **options):
        dry_run  = options["dry_run"]
        force    = options["force"]
        event_id = options["event_id"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no LLM calls will be made\n"))

        # --- Candidate selection ------------------------------------------
        if event_id:
            candidates = Event.objects.select_related("event_list").filter(pk=event_id)
        else:
            now = timezone.now()
            # Events that are in the past and don't have a published AIRating
            published_event_ids = AIRating.objects.filter(
                status=AIRating.STATUS_PUBLISHED
            ).values_list("event_id", flat=True)

            qs = Event.objects.select_related("event_list").filter(
                date_time__lt=now,
            ).exclude(
                id__in=published_event_ids,
            )

            if not force:
                # Also exclude events already pending/flagged unless --force
                already_rated_ids = AIRating.objects.values_list("event_id", flat=True)
                qs = qs.exclude(id__in=already_rated_ids)

            candidates = qs.order_by("date_time")

        total     = candidates.count()
        checked   = 0
        finished  = 0
        processed = 0
        flagged   = 0
        skipped   = 0
        errors    = 0

        self.stdout.write(f"Checking {total} candidate event(s)...\n")

        for event in candidates:
            checked += 1

            # --- Finished check -------------------------------------------
            # Single-event mode (--event-id) bypasses the API status check
            if event_id:
                event_finished = True
            else:
                event_finished = event.is_finished or is_event_finished(event)

            if not event_finished:
                self.stdout.write(f"  [{checked}/{total}] SKIP (not finished): {event}")
                skipped += 1
                continue

            finished += 1

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f"  [{checked}/{total}] WOULD PROCESS: {event}")
                )
                continue

            # --- Run pipeline ---------------------------------------------
            self.stdout.write(f"  [{checked}/{total}] Processing: {event}")
            try:
                ai_rating = run_pipeline(event, force=force)
                processed += 1

                status_style = (
                    self.style.ERROR   if ai_rating.status == AIRating.STATUS_FLAGGED
                    else self.style.SUCCESS
                )
                flag_note = (
                    f"  ⚠  Flagged: {'; '.join(ai_rating.flag_reasons)}"
                    if ai_rating.status == AIRating.STATUS_FLAGGED else ""
                )
                self.stdout.write(
                    status_style(
                        f"    → {ai_rating.stars}★  {ai_rating.verdict}"
                        f"  [{ai_rating.status}]{flag_note}"
                    )
                )
                self.stdout.write(f"    Blurb: {ai_rating.blurb}")

                if ai_rating.status == AIRating.STATUS_FLAGGED:
                    flagged += 1

            except PipelineError as exc:
                errors += 1
                self.stdout.write(self.style.ERROR(f"    ERROR: {exc}"))
                logger.error("run_ratings: pipeline error for event pk=%s: %s", event.pk, exc)
            except Exception as exc:
                errors += 1
                self.stdout.write(self.style.ERROR(f"    UNEXPECTED ERROR: {exc}"))
                logger.exception("run_ratings: unexpected error for event pk=%s", event.pk)

        # --- Summary ------------------------------------------------------
        self.stdout.write("\n" + "─" * 50)
        self.stdout.write(f"Candidates:  {total}")
        self.stdout.write(f"Checked:     {checked}")
        self.stdout.write(f"Not finished:{skipped}")
        self.stdout.write(f"Finished:    {finished}")
        if not dry_run:
            self.stdout.write(f"Processed:   {processed}")
            if flagged:
                self.stdout.write(self.style.WARNING(f"Flagged:     {flagged}  ← manual review needed"))
            if errors:
                self.stdout.write(self.style.ERROR(f"Errors:      {errors}"))
