from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from core.models import Event, Rating


class HomeView(View):
    def get(self, request):
        # Get todays events
        now = timezone.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        last_week = now - timedelta(days=7)

        recent_ratings = Rating.objects.all().order_by('-id')[:10]
        recent_voted_events = []

        for rating in recent_ratings:
            event = rating.event
            league = event.event_list.league  # Get the league for this event
            recent_voted_events.append({
                'event': event,
                'league': league,
        })
            
        todays_events = Event.objects.filter(date_time__range=(today, tomorrow)).order_by('date_time')
        recent_events = Event.objects.filter(date_time__range=(last_week, now)).order_by('-date_time')
        
        context = {
            'installed': settings.INSTALLED_APPS,
            'recent_voted_events': recent_voted_events,
            'todays_events': todays_events,
            'recent_events': recent_events,
        }
        
        return render(request, 'home/home.html', context)


def events_more(request):
    # Get the next batch of events
    offset = int(request.GET.get('offset', 0))
    events = Event.objects.filter(date_time__gte=timezone.now()).order_by('date_time')[offset:offset+10]

    # Return a JSON response
    return JsonResponse({'events': [{'id': event.id, 'event_list': event.event_list.name, 'event': event.event, 'event_type': event.event_type, 'date_time': event.date_time} for event in events]})


def about_view(request):
    return render(request, 'home/about.html')

def replay_platforms_view(request):
    return render(request, 'home/replay_platforms.html')