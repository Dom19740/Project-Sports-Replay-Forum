from django.shortcuts import render, get_object_or_404
from .models import RaceWeekend, Event

def race_weekend_list(request):
    race_weekends = RaceWeekend.objects.all()
    return render(request, 'f1/race_weekend_list.html', {'race_weekends': race_weekends})

def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'f1/event_detail.html', {'event': event})
