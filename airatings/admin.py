from django.contrib import admin
from .models import AIRating, EventSignals


@admin.register(AIRating)
class AIRatingAdmin(admin.ModelAdmin):
    list_display  = ("event", "stars", "verdict", "status", "created_at")
    list_filter   = ("status", "verdict", "stars")
    search_fields = ("event__event_list__name", "event__event_type")
    readonly_fields = (
        "event", "stars", "verdict", "blurb",
        "rationale_internal", "flag_reasons", "created_at", "updated_at",
    )
    fields = (
        "event", "status",
        "stars", "verdict", "blurb",
        "rationale_internal", "flag_reasons",
        "created_at", "updated_at",
    )
    # status is the only writable field — human approval gate for Phase 8


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
