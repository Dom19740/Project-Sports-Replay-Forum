from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.db.models import ExpressionWrapper
from django.db import models
from core.models import Event, Rating

class HomeView(View):
    def get(self, request):
        print(request.get_host())
        host = request.get_host()
        islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0
        context = {
            'installed': settings.INSTALLED_APPS,
            'islocal': islocal
        }

        # Get the last events to receive a vote
        recent_ratings = Rating.objects.all().order_by('-id')[:5]
        recent_voted_events = []
        for rating in recent_ratings:
            if rating.event not in recent_voted_events:
                recent_voted_events.append(rating.event)

        # Get the top most rated events
        most_rated_events = Event.objects.annotate(
            total_votes=ExpressionWrapper(
                models.F('rating__five_stars') + models.F('rating__four_stars') + models.F('rating__three_stars') + models.F('rating__two_stars') + models.F('rating__one_star'),
                output_field=models.IntegerField()
            )
        ).order_by('-total_votes')[:5]
        
        context = {
            'recent_voted_events': recent_voted_events,
            'most_rated_events': most_rated_events,
        }

        return render(request, 'home/main.html', context)
