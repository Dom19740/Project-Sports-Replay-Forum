from django.contrib import admin
from .models import EventSignals


@admin.register(EventSignals)
class EventSignalsAdmin(admin.ModelAdmin):
    """
    INTERNAL ONLY. These signals are LLM-generated from spoiler-full data.
    Never expose signals or one_line_internal_note to users.
    """
    list_display  = ("event", "excitement", "drama", "competitiveness", "created_at")
    readonly_fields = ("event", "signals", "created_at", "updated_at")
    list_filter   = ("created_at",)

    def _sig(self, obj, key, default=None):
        return (obj.signals or {}).get(key, default)

    def excitement(self, obj):
        return self._sig(obj, "excitement")
    excitement.short_description = "Excitement"

    def drama(self, obj):
        return self._sig(obj, "drama")
    drama.short_description = "Drama"

    def competitiveness(self, obj):
        return self._sig(obj, "competitiveness")
    competitiveness.short_description = "Competitive"
