from django.contrib import admin
from .models import UserProfile, XPEvent, Badge, UserBadge


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_xp', 'current_level', 'current_streak', 'longest_streak', 'last_active_date']
    search_fields = ['user__username']
    ordering = ['-total_xp']


@admin.register(XPEvent)
class XPEventAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'amount', 'related_event', 'created']
    list_filter = ['action_type']
    search_fields = ['user__username']
    ordering = ['-created']


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'rarity_threshold', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
    search_fields = ['user__username', 'badge__name']
