
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
    rating_text = {
        5: "Amazing! Definitely Worth Watching the Full Replay",
        4: "",
        3: "Pretty Good! Worth Watching the Highlights",
        2: "",
        1: "Not great! Just Check the Results"
    }
    return render(request, 'f1/race_event.html', {'event': event, 'rating_text': rating_text})


def vote(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    rating, created = Rating.objects.get_or_create(event=event)

    if request.method == 'POST':
        rating_type = request.POST.get('stars')
        if rating_type == '5':
            rating.five_stars += 1
        elif rating_type == '4':
            rating.four_stars += 1
        elif rating_type == '3':
            rating.three_stars += 1
        elif rating_type == '2':
            rating.two_stars += 1
        elif rating_type == '1':
            rating.one_star += 1

        # Calculate the total votes
        total_votes = (
            rating.five_stars + 
            rating.four_stars + 
            rating.three_stars + 
            rating.two_stars + 
            rating.one_star
        )

        # Calculate the total score based on percentage values
        weighted_average = (
            (rating.five_stars * 90) + 
            (rating.four_stars * 70) + 
            (rating.three_stars * 50) + 
            (rating.two_stars * 30) + 
            (rating.one_star * 10)
        ) / total_votes

        # Scale the weighted average to a range of 1 to 100
        if total_votes > 0:
            rating.percentage = weighted_average
        else:
            rating.percentage = 0.0  # Handle no votes

        # Debugging outputs
        print(f"Total Votes: {total_votes}")
        print(f"Final Percentage: {rating.percentage}")

        rating.save()

    return redirect('event', event_id=event_id)