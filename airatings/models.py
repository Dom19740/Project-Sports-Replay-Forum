from django.db import models
from core.models import Event


class AIRating(models.Model):
    """
    Final pipeline output for one event.
    blurb is the only field safe to expose to users.
    rationale_internal is INTERNAL ONLY — never shown to users.
    """

    STATUS_PENDING  = "pending_review"
    STATUS_PUBLISHED = "published"
    STATUS_FLAGGED  = "flagged"
    STATUS_CHOICES  = [
        (STATUS_PENDING,   "Pending Review"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_FLAGGED,   "Flagged — Manual Review Required"),
    ]

    # related_name avoids colliding with Event.ai_rating (legacy CharField)
    event              = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="ai_pipeline")
    status             = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    stars              = models.IntegerField()
    verdict            = models.CharField(max_length=20)
    blurb              = models.TextField()
    rationale_internal = models.TextField()
    flag_reasons       = models.JSONField(default=list, blank=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "AI Rating"
        verbose_name_plural = "AI Ratings"

    def __str__(self):
        return f"{self.stars}★ {self.verdict} [{self.status}] — {self.event}"


class EventSignals(models.Model):
    """
    Stage-one LLM output: spoiler-full excitement signals.
    INTERNAL ONLY — never exposed to users.
    """
    event      = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="signals")
    signals    = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "⚠ Event Signals [INTERNAL]"
        verbose_name_plural = "⚠ Event Signals [INTERNAL]"

    def __str__(self):
        return f"Signals for {self.event}"
