from django.shortcuts import render, get_object_or_404
from .models import RaceWeekend, Event

def race_weekend_list(request):
    race_weekends = RaceWeekend.objects.all()
    return render(request, 'f1/race_weekend_list.html', {'race_weekends': race_weekends})
