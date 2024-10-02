
from .models import Race, Event,Event, Rating
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg

def race_list(request):
    races = Race.objects.all()
    return render(request, 'f1/race_list.html', {'races': races})


def race_events(request, race_id):
    race = get_object_or_404(Race, id=race_id)
    events = Event.objects.filter(race_weekend=race)
    return render(request, 'f1/race_weekend.html', {'events': events, 'race': race})


def event_list(request):
    events = Event.objects.all().order_by('date_time')
    return render(request, 'f1/event_list.html', {'events': events})


# View to handle rating submission and display form
@login_required
def rate_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Check if the user has already rated the event
    existing_rating = Rating.objects.filter(event=event, user=request.user).first()

    if request.method == 'POST':
        score = int(request.POST.get('score'))

        # If the user already rated, prevent re-rating
        if existing_rating:
            messages.error(request, 'You have already rated this event.')
            return redirect('event_results', event_id=event.id)

        # Validate and create new rating
        if 1 <= score <= 3:
            Rating.objects.create(event=event, user=request.user, score=score)
            messages.success(request, 'Your rating has been submitted.')
            return redirect('event_results', event_id=event.id)
        else:
            messages.error(request, 'Invalid rating score. Please choose between 1 and 3.')

    return render(request, 'rate_event.html', {'event': event, 'existing_rating': existing_rating})

# View to show the average rating for an event
def event_results(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    ratings = Rating.objects.filter(event=event)

    # Calculate average score
    avg_rating = ratings.aggregate(average=Avg('score'))['average'] or 0
    avg_rating = round(avg_rating, 2)  # Round to 2 decimal places for display

    return render(request, 'event_results.html', {'event': event, 'ratings': ratings, 'avg_rating': avg_rating})
