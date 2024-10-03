from django.contrib import admin
from .models import Race, Event, Rating

# Register the Race model
@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')

# Register the Event model
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'race_weekend', 'date_time')

# Register the Rating model (optional, just for viewing in admin)
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('event', 'five_stars', 'four_stars', 'three_stars', 'two_stars', 'one_star', 'percentage', 'get_voters')

    def get_voters(self, obj):
        return ', '.join([voter.username for voter in obj.voters.all()])
    get_voters.short_description = 'Voters'