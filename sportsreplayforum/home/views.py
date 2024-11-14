from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.db.models import Q
from django.db import models
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
            if rating.event not in recent_voted_events:
                recent_voted_events.append(rating.event)

        # Get the next 5 events that will occur
        now = datetime.now()
        last_events = Event.objects.filter(date_time__lte=now).order_by('-date_time')[:5]

        context = {
            'installed': settings.INSTALLED_APPS,
            'islocal': islocal,
            'recent_voted_events': recent_voted_events,
            'last_events': last_events,
        }
        return render(request, 'home/home.html', context)

def about_view(request):
    return render(request, 'home/about.html')