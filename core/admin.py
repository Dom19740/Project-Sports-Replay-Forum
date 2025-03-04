from django.contrib import admin
from .models import Competition, Event, Rating, Comment


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('league', 'name', 'date')
    list_filter = ('league', 'date')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_list', 'date_time', 'get_league', 'event_type', 'idEvent', 'video_id', 'is_finished')
    list_filter = ('event_list__league', 'date_time', 'is_finished', 'event_type')

    def get_league(self, obj):
        return obj.event_list.league
    get_league.short_description = 'League'
    get_league.admin_order_field = 'event_list__league'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('event', 'five_stars', 'four_stars', 'three_stars', 'two_stars', 'one_star', 'percentage', 'get_voters', 'likes', 'dislikes')
    list_filter = ('five_stars', 'four_stars', 'three_stars', 'two_stars', 'one_star', 'percentage')

    def get_voters(self, obj):
        return ', '.join([voter.username for voter in obj.voters.all()])
    get_voters.short_description = 'Voters'


@admin.register(Comment)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('author', 'parent_post', 'body', 'created')
    list_filter = ('author', 'created')
    search_fields = ('author', 'parent_post', 'body')
    date_hierarchy = 'created'
