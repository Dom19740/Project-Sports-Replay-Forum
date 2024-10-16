from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.urls import reverse
from .forms import LoginForm, RegisterForm
from .models import Competition, Event, Rating
from datetime import timedelta
import urllib

# db league names converted to Titles  
TITLES = {
    'Formula 1': 'FIA F1 World Championship',
    'UEFA Nations League': 'UEFA Nations League',
    'UEFA Champions League': 'UEFA Champions League',
    'English Premier League': 'Premier League',
    'MotoGP': 'MotoGP',
    'FIFA World Cup': 'FIFA World Cup'
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

    upcoming_competitions = upcoming_competitions[:5]
    past_competitions = past_competitions[:25]

    upcoming_competitions.reverse()

    return render(request, 'core/competition_schedule.html', {
        'title': title,
        'upcoming_competitions': upcoming_competitions,
        'past_competitions': past_competitions,
        'league': league,
    })


def event_list(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    events = Event.objects.filter(event_list=competition).order_by('-date_time')

    upcoming_events = []
    past_events = []

    current_time = timezone.now()
    threshold = timedelta(minutes=45)

    for event in events:
        if event.date_time + threshold <= current_time:
            past_events.append(event)
        else:
            upcoming_events.append(event)

    upcoming_events.reverse()

    title = TITLES.get(competition.league, 'Unknown League')

    return render(request, 'core/event_list.html', {
        'events_combined': [
            {'type': 'Past', 'events': past_events},
            {'type': 'Upcoming', 'events': upcoming_events},
        ],
        'competition': competition,
        'title': title,
        'league': competition.league,
    })


def event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    rating_text = {
        5: "Hot! Definitely Worth Watching the Full Replay",
        4: "",
        3: "Mid temp! Worth Watching the Highlights",
        2: "",
        1: "Cold! Just Check the Results"
    }

    video_id = event.video_id.split('=')[-1] if event.video_id else None

    title = TITLES.get(event.event_list.league, 'Unknown League')

    return render(request, 'core/event.html', {
        'event': event,
        'rating_text': rating_text,
        'video_id': video_id,
        'title': title,
        'timezone': timezone,
        'timedelta': timedelta,
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


def sign_in(request):

    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('home')

        next_url = request.GET.get('next')
        form = LoginForm()
        return render(request,'core/login.html', {'form': form, 'next': next_url})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}, welcome back!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('home')
        
        # If the form is not valid, log the error
        messages.error(request,f'Invalid username or password')
        return render(request,'core/login.html',{'form': form})
    

def sign_out(request):
    logout(request)
    next_url = request.GET.get('next')
    print(f"Next URL: {next_url}")  # Add this line to print the next URL
    if next_url:
        return redirect(next_url)
    else:
        return redirect('home')
    

def sign_up(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            messages.success(request, 'You have registered up successfully.')
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')
    else:
        next_url = request.GET.get('next')
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form, 'next': next_url})


# Define your search terms globally or in the view
search_terms = {
    'f1': ['formula 1'],
    'football': ['premier', 'nations', 'champions'],
    'motorsport': ['motogp', 'formula 1'],
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
            league_urls[league_name] = reverse('core:competition_schedule') + '?league=' + urllib.parse.quote(league_name)
    else:
        competitions = Competition.objects.none()
        events = Event.objects.none()
        leagues = Competition.objects.none()
        league_urls = {}

    return render(request, 'core/search_results.html', {
        'competitions': competitions,
        'events': events,
        'league_urls': league_urls,
        'query': q,
    })
