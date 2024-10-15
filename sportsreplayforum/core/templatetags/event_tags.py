from django import template
from datetime import timedelta
from django.utils import timezone

register = template.Library()

@register.filter
def is_past(event):
    return event.date_time + timedelta(minutes=45) <= timezone.now()