
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
    print(events)  # Add this line to print out the events

    return render(request, 'f1/race_weekend.html', {'events': events, 'race': race})


def event_list(request):
    events = Event.objects.all().order_by('date_time')
    return render(request, 'f1/event_list.html', {'events': events})

