from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import Event, Rating
from core.views import sports
from django.core.paginator import Paginator

class HomeView(View):
    def get(self, request):
        print(request.get_host())
        host = request.get_host()
        islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0

        # Get the last events to receive a vote
        recent_ratings = Rating.objects.all().order_by('-id')[:6]
        recent_voted_events = []
        
        for rating in recent_ratings:
            event = rating.event
            league = event.event_list.league  # Get the league for this event
            recent_voted_events.append({
                'event': event,
                'league': league
        })

        # Get todays events
        now = timezone.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)

        last_events = Event.objects.filter(date_time__range=(datetime.combine(today, datetime.min.time()), datetime.combine(tomorrow, datetime.min.time()))).order_by('date_time')

        paginator = Paginator(last_events, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        last_events_list = [{'event': event, 'league': event.event_list.league} for event in page_obj]

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
            'page_obj': page_obj,
        }
        
        return render(request, 'home/home.html', context)
    

def about_view(request):
    return render(request, 'home/about.html')