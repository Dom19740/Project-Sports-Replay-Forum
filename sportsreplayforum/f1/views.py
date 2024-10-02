
from .models import Race, Event,Event, Rating
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg



def race_list(request):
    races = Race.objects.all()
    for race in races:
        events = Event.objects.filter(race_weekend=race)
        race.start_date = events.order_by('date_time').first().date_time
        race.end_date = events.order_by('-date_time').first().date_time
    return render(request, 'f1/race_list.html', {'races': races})


def race_weekend(request, race_id):
    race = get_object_or_404(Race, id=race_id)
    events = Event.objects.filter(race_weekend=race).order_by('-date_time')

    return render(request, 'f1/race_weekend.html', {'events': events, 'race': race})


def event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'f1/race_event.html', {'event': event})


def vote(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    rating, created = Rating.objects.get_or_create(event=event)

    if request.method == 'POST':
        rating_type = request.POST.get('stars')
        if rating_type == '3':
            rating.three_stars += 1
        elif rating_type == '2':
            rating.two_stars += 1
        elif rating_type == '1':
            rating.one_star += 1
        rating.save()

    return redirect('event', event_id=event_id)