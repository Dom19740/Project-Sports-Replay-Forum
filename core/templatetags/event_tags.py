from django import template
from datetime import timedelta
from django.utils import timezone

register = template.Library()

@register.filter
def is_past(event):
    return event.date_time + timedelta(minutes=45) <= timezone.now()

@register.filter
def voting_closed(event):
    return event.date_time + timedelta(days=7) <= timezone.now()

@register.filter
def format_comment_date(value):
    if not value:
        return ''
    now = timezone.now()
    diff = now - value
    seconds = diff.total_seconds()

    if seconds < 24 * 3600:

        if seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes}m ago" if minutes != 1 else "1m ago"
        else:
            hours = int(seconds // 3600)
            return f"{hours}h ago" if hours != 1 else "1h ago"

    return value.strftime("%b %d %Y")