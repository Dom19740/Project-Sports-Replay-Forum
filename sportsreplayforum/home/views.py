from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from core.models import Event, Rating
from core.views import sports

class HomeView(View):
    def get(self, request):
        print(request.get_host())
        host = request.get_host()
        islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0

        # Get the last events to receive a vote
        recent_ratings = Rating.objects.all().order_by('-id')[:5]
        recent_voted_events = []
        
        for rating in recent_ratings:
            event = rating.event
            league = event.event_list.league  # Get the league for this event
            recent_voted_events.append({
                'event': event,
                'league': league
        })

        # Get the next 5 events that will occur
        now = timezone.now()
        last_events = Event.objects.filter(date_time__lte=now).order_by('-date_time')[:5]
        last_events_list = []
        
        for event in last_events:
            league = event.event_list.league  # Get the league for this event
            last_events_list.append({
                'event': event,
                'league': league
        })

        context = {
            'installed': settings.INSTALLED_APPS,
            'islocal': islocal,
            'recent_voted_events': recent_voted_events,
            'last_events': last_events_list,
        }
        
        return render(request, 'home/home.html', context)
    

def about_view(request):
    return render(request, 'home/about.html')