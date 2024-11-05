from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.core.management import call_command
from django.conf import settings
from .models import Competition, Event, Rating
from datetime import timedelta


# db league names converted to Titles  
TITLES = {
    'Formula 1': 'Formula 1 World Championship',
    'UEFA Champions League': 'UEFA Champions League',
    'English Premier League': 'English Premier League',
    'MotoGP': 'MotoGP',
    'NASCAR Cup Series': 'NASCAR Cup Series',
    'IndyCar Series': 'IndyCar Series',
}

RATINGS_TEXT = {
    5: "Hot Watch! Definitely Watch the Full Replay",
    4: "",
    3: "Mid Temp! Worth Watching the Highlights",
    2: "",
    1: "Not Watch! Just Check Out the Results"
}


def competition_schedule(request, league):

    today = timezone.now()
    title = TITLES.get(league, 'Unknown League')

    competitions = Competition.objects.order_by('-date').filter(league=league)

    upcoming_competitions = []
    past_competitions = []
    
    for competition in competitions:
        events = Event.objects.filter(event_list=competition)
        if events.exists():
            competition.start_date = events.order_by('date_time').first().date_time
            competition.end_date = events.order_by('-date_time').first().date_time

            if competition.start_date >= today:
                upcoming_competitions.append(competition)
            else:
                past_competitions.append(competition)

    upcoming_competitions.reverse()

    upcoming_competitions = upcoming_competitions[:5]
    past_competitions = past_competitions[:5]
    banner = competition.banner
    badge = competition.badge
    
    return render(request, 'core/competition_schedule.html', {
        'title': title,
        'upcoming_competitions': upcoming_competitions,
        'past_competitions': past_competitions,
        'league': league,
        'banner': banner,
        'badge': badge,
    })


def event_list(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    events = Event.objects.filter(event_list=competition).order_by('-date_time')

    events_upcoming = []
    events_past = []

    current_time = timezone.now()
    threshold = timedelta(minutes=45)

    for event in events:
        if event.date_time + threshold <= current_time:
            events_past.append(event)
        else:
            events_upcoming.append(event)

    events_upcoming.reverse()

    title = TITLES.get(competition.league, 'Unknown League')
    banner = competition.banner

    return render(request, 'core/event_list.html', {
        'events_upcoming': events_upcoming,
        'events_past': events_past,
        'competition': competition,
        'title': title,
        'league': competition.league,
        'banner': banner,
    })


def event(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    video_id = event.video_id.split('=')[-1] if event.video_id else None

    title = TITLES.get(event.event_list.league, 'Unknown League')

    results = event.results.all()
    poster = event.poster

    try:
        total_votes = (
            event.rating.five_stars + 
            event.rating.four_stars + 
            event.rating.three_stars + 
            event.rating.two_stars + 
            event.rating.one_star
        )
    except Event.rating.RelatedObjectDoesNotExist:
        total_votes = 0

    return render(request, 'core/event.html', {
        'event': event,
        'RATINGS_TEXT': RATINGS_TEXT,
        'video_id': video_id,
        'title': title,
        'timezone': timezone,
        'timedelta': timedelta,
        'total_votes': total_votes,
        'results': results,
        'poster': poster,
    })


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

    return redirect('core:event', event_id=event_id)

def replay_platforms(request):
    return render(request, 'core/replay_platforms.html')


# Define your search terms globally or in the view
search_terms = {
    'f1': ['formula 1'],
    'football': ['premier', 'nations', 'champions'],
    'motorsport': ['motogp', 'formula 1', 'NASCAR', 'IndyCar'],
}

search_terms['motor'] = search_terms['motorsport']


def search(request):
    q = request.GET.get('q')
    if q:
        # Check if the query matches any of the predefined search terms
        if q.lower() in search_terms:
            # Use the corresponding terms for querying
            search_keywords = search_terms[q.lower()]
        else:
            # If no predefined term is found, use the query directly
            search_keywords = [q]

        # Query the database for each search keyword
        competitions = Competition.objects.filter(
            name__icontains=search_keywords[0]
        )
        for term in search_keywords[1:]:
            competitions |= Competition.objects.filter(name__icontains=term)

        events = Event.objects.filter(
            event_type__icontains=search_keywords[0]
        )
        for term in search_keywords[1:]:
            events |= Event.objects.filter(event_type__icontains=term)

        leagues = Competition.objects.filter(
            league__icontains=search_keywords[0]
        ).values('league').distinct()
        for term in search_keywords[1:]:
            leagues |= Competition.objects.filter(league__icontains=term).values('league').distinct()

        # Generate league URLs
        league_urls = {}
        for league in leagues:
            league_name = league['league']
            league_urls[league_name] = reverse('core:competition_schedule', kwargs={'league': league_name})

        # Pass a default league argument to the template
        league = None
        if leagues:
            league = leagues[0]['league']
    else:
        competitions = Competition.objects.none()
        events = Event.objects.none()
        leagues = Competition.objects.none()
        league_urls = {}
        league = None

    return render(request, 'core/search_results.html', {
        'competitions': competitions,
        'events': events,
        'league_urls': league_urls,
        'query': q,
        'league': league,  # Pass the league argument to the template
    })


def run_populate(request, command, success_message):
    token = request.GET.get('token', '')

    # Compare the token with the one stored in settings
    if token != settings.API_PULL_TOKEN:
        return JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=403)

    try:
        call_command(command)
        return JsonResponse({'status': 'success', 'message': success_message})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
