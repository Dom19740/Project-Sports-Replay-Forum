from django.db import models
from core.models import Event


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
