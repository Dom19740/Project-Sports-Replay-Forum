# Copyright (c) 2024 dpb creative
# This code is licensed for non-commercial use only. See LICENSE file for details.

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Competition, Event, Rating, Comment
from users.forms import CreateCommentForm, CreateReplyForm
from datetime import timedelta
from pyexpat.errors import messages

sports = [
    {'name': 'Formula 1', 'title': 'F1', 'logo': 'logo_f1.png'},
    {'name': 'MotoGP', 'title': 'MotoGP', 'logo': 'logo_motogp.png'},
    {'name': 'IndyCar Series', 'title': 'IndyCar', 'logo': 'logo_indy.png'},
    {'name': 'NASCAR Cup Series', 'title': 'NASCAR', 'logo': 'logo_nascar.png'},
    {'name': 'English Premier League', 'title': 'Premier League', 'logo': 'logo_premier.png'},
    {'name': 'UEFA Champions League', 'title': 'Champions League', 'logo': 'logo_champions.png'},
    # {'name': 'NFL', 'title': 'NFL', 'logo': 'logo_nfl.png'},
    # {'name': 'NBA', 'title': 'NBA', 'logo': 'logo_nba.png'},
    # {'name': 'NHL', 'title': 'NHL', 'logo': 'logo_nhl.png'},
]

search_terms = {
    'f1': ['formula 1'],
    'football': ['premier', 'nations', 'champions'],
    'motorsport': ['motogp', 'formula 1', 'NASCAR', 'IndyCar'],
}

search_terms['motor'] = search_terms['motorsport']

RATINGS_TEXT = {
    5: "Hot Watch!",
    4: "",
    3: "Mid Temp!",
    2: "",
    1: "Not Watch!"
}


def competition_schedule(request, league):

    today = timezone.now()
    title = next((sport['name'] for sport in sports if sport['name'] == league), 'Unknown League')

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
    badge = next((sport['logo'] for sport in sports if sport['name'] == league), 'default_logo.png')
    
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

    title = next((sport['name'] for sport in sports if sport['name'] == competition.league), 'Unknown League')
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

    title = next((sport['name'] for sport in sports if sport['name'] == event.event_list.league), 'Unknown League')
    poster = event.poster
    ai_review = event.ai_review
    ai_rating = event.ai_rating
    comments = event.comments.all()

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

    commentform = CreateCommentForm()

    context = {
        'event': event,
        'RATINGS_TEXT': RATINGS_TEXT,
        'video_id': video_id,
        'title': title,
        'timezone': timezone,
        'timedelta': timedelta,
        'total_votes': total_votes,
        'poster': poster,
        'ai_review': ai_review,
        'ai_rating': ai_rating,
        'comments': comments,
        'commentform': commentform,
    }

    return render(request, 'core/event.html', context)


def vote(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    rating, created = Rating.objects.get_or_create(event=event)

    if request.method == 'POST':
        if 'stars' in request.POST:
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

            total_votes = (
                rating.five_stars + 
                rating.four_stars + 
                rating.three_stars + 
                rating.two_stars + 
                rating.one_star
            )

            # Calculate the total score based on normalized weights
            weighted_average = (
                (rating.five_stars * 5) + 
                (rating.four_stars * 4) + 
                (rating.three_stars * 3) + 
                (rating.two_stars * 2) + 
                (rating.one_star * 1)
            ) / total_votes

            # Scale the weighted average to a range of 1 to 100
            if total_votes > 0:
                rating.percentage = (weighted_average / 5) * 100
            else:
                rating.percentage = 0.0  # Handle no votes

            rating.save()
            rating.voters.add(request.user)

        like_type = None
        if 'like' in request.POST:
            like_type = 'liked'
        elif 'dislike' in request.POST:
            like_type = 'disliked'

        if like_type:
            current_vote = request.COOKIES.get(f'voted_{event_id}')
            if current_vote != like_type:
                if current_vote == 'liked':
                    rating.likes -= 1
                elif current_vote == 'disliked':
                    rating.dislikes -= 1

                if like_type == 'liked':
                    rating.likes += 1
                elif like_type == 'disliked':
                    rating.dislikes += 1

                rating.save()
                response = redirect('core:event', event_id=event_id)
                response.set_cookie(f'voted_{event_id}', like_type, max_age=365*24*60*60)
                return response

    return redirect('core:event', event_id=event_id)


def search(request):
    q = request.GET.get('q')
    if q:
        if q.lower() in search_terms:
            search_keywords = search_terms[q.lower()]
        else:
            search_keywords = [q]

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

        league_urls = {}
        for league in leagues:
            league_name = league['league']
            league_urls[league_name] = reverse('core:competition_schedule', kwargs={'league': league_name})

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
        'league': league,
    })


def run_populate(request, command, success_message):
    token = request.GET.get('token', '')

    if token != settings.API_PULL_TOKEN:
        return JsonResponse({'status': 'error', 'message': 'Invalid token'}, status=403)

    try:
        call_command(command)
        return JsonResponse({'status': 'success', 'message': success_message})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def comment_sent(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.event = event
            comment.author = request.user
            comment.save()
    
    return redirect('core:event', event_id=event.id)


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    event = comment.event  # Get the event from the comment
    if request.user == comment.author:
        comment.delete()
    return redirect('core:event', event_id=event.id)
