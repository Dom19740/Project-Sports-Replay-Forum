
from .models import Competition, Event,Event, Rating
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg



def competition_schedule(request):
    competitions = Competition.objects.order_by('-date')
    for competition in competitions:
        events = Event.objects.filter(event_list=competition)
        competition.start_date = events.order_by('date_time').first().date_time
        competition.end_date = events.order_by('-date_time').first().date_time
    return render(request, 'f1/competition_schedule.html', {'competitions': competitions})


def event_list(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    events = Event.objects.filter(event_list=competition).order_by('-date_time')

    return render(request, 'f1/event_list.html', {'events': events, 'competition': competition})


def event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    rating_text = {
        5: "Hot! Definitely Worth Watching the Full Replay",
        4: "",
        3: "Mid temp! Worth Watching the Highlights",
        2: "",
        1: "Cold! Just Check the Results"
    }
    return render(request, 'f1/event.html', {'event': event, 'rating_text': rating_text})


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

        rating.save()
        rating.voters.add(request.user)

    return redirect('event', event_id=event_id)