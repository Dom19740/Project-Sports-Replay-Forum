# Copyright (c) 2024 dpb creative
# This code is licensed for non-commercial use only. See LICENSE file for details.

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Competition, Event, Rating, Comment, Reply, CommentVote
from gamify.services import award_xp
from gamify.badges import check_badges
from gamify.notifications import queue_notification
from users.forms import CreateCommentForm, CreateReplyForm
from datetime import timedelta
from pyexpat.errors import messages

#COMMENT OUT SPORTS HERE IF YOU WANT TO REMOVE THEM FROM THE SITE
sports = [
    {'name': 'FIFA World Cup', 'title': 'FIFA World Cup', 'logo': 'logo_FIFA World Cup.png'},
    {'name': 'Formula 1', 'title': 'F1', 'logo': 'logo_f1.png'},
    {'name': 'MotoGP', 'title': 'MotoGP', 'logo': 'logo_motogp.png'},
    #{'name': 'IndyCar Series', 'title': 'IndyCar', 'logo': 'logo_indy.png'},
    #{'name': 'NASCAR Cup Series', 'title': 'NASCAR', 'logo': 'logo_nascar.png'},
    ##{'name': 'UEFA Champions League', 'title': 'Champions League', 'logo': 'logo_champions.png'},
    #{'name': 'UEFA Europa League', 'title': 'Europa League', 'logo': 'logo_europa.png'},
    #{'name': 'English Premier League', 'title': 'Premier League', 'logo': 'logo_premier.png'},
    #{'name': 'Scottish Premier League', 'title': 'SPL', 'logo': 'logo_spl.png'},
    # {'name': 'NFL', 'title': 'NFL', 'logo': 'logo_nfl.png'},
    #{'name': 'NBA', 'title': 'NBA', 'logo': 'logo_nba.png'},
    #{'name': 'NHL', 'title': 'NHL', 'logo': 'logo_nhl.png'},
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
        events = Event.objects.filter(event_list=competition).order_by('date_time')
        if events.exists():
            competition.start_date = events.first().date_time
            competition.end_date = events.last().date_time
            competition.events_list = list(events)

            race_event = next((e for e in competition.events_list if e.event_type == 'Race'), competition.events_list[0])
            try:
                competition.main_rating = race_event.rating.average_stars
                competition.main_rating_label = race_event.rating.star_label
            except Exception:
                competition.main_rating = None
                competition.main_rating_label = None

            if competition.start_date >= today:
                upcoming_competitions.append(competition)
            else:
                past_competitions.append(competition)

    upcoming_competitions.reverse()

    upcoming_competitions = upcoming_competitions[:5]
    past_competitions = past_competitions[:5]
    banner = competition.banner
    badge = next((sport['logo'] for sport in sports if sport['name'] == league), 'default_logo.png')

    context = {
        'title': title,
        'upcoming_competitions': upcoming_competitions,
        'past_competitions': past_competitions,
        'league': league,
        'banner': banner,
        'badge': badge,
    }

    if league == 'FIFA World Cup':
        context['upcoming_events'] = Event.objects.filter(
            event_list__league='FIFA World Cup',
            date_time__gte=today,
        ).order_by('date_time')[:8]
        context['past_events'] = Event.objects.filter(
            event_list__league='FIFA World Cup',
            date_time__lt=today,
        ).order_by('-date_time')[:8]

    return render(request, 'core/competition_schedule.html', context)


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
    comments = event.comments.prefetch_related('replies').annotate(
        like_count=Count('votes', filter=Q(votes__vote='like')),
        dislike_count=Count('votes', filter=Q(votes__vote='dislike')),
    ).all()
    commentform = CreateCommentForm()
    replyform = CreateReplyForm()

    if request.user.is_authenticated:
        user_comment_votes = {
            str(v.comment_id): v.vote
            for v in CommentVote.objects.filter(user=request.user, comment__event=event)
        }
    else:
        user_comment_votes = {}

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

    has_voted = request.COOKIES.get(f'voted_{event_id}', False)

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
        'replyform': replyform,
        'has_voted': has_voted,
        'user_comment_votes': user_comment_votes,
    }

    return render(request, 'core/event.html', context)


def vote(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    rating, created = Rating.objects.get_or_create(event=event)

    if request.method == 'POST':
        if 'stars' in request.POST:
            current_vote = request.COOKIES.get(f'voted_{event_id}')
            if current_vote:
                return redirect('core:event', event_id=event_id)  # User has already voted

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

            if request.user.is_authenticated:
                xp_result = award_xp(request.user, 'event_rated', event)
                new_badges = check_badges(request.user)
                queue_notification(request, xp_result, new_badges)

            response = redirect('core:event', event_id=event_id)
            response.set_cookie(f'voted_{event_id}', 'true', max_age=365*24*60*60)
            return response

        if 'like' in request.POST or 'dislike' in request.POST:
            like_type = None
            if 'like' in request.POST:
                like_type = 'liked'
            elif 'dislike' in request.POST:
                like_type = 'disliked'

            if like_type:
                current_like = request.COOKIES.get(f'liked_{event_id}')
                if current_like != like_type:
                    if current_like == 'liked':
                        rating.likes -= 1
                    elif current_like == 'disliked':
                        rating.dislikes -= 1

                    if like_type == 'liked':
                        rating.likes += 1
                    elif like_type == 'disliked':
                        rating.dislikes += 1

                    rating.save()

                    if request.user.is_authenticated:
                        xp_result = award_xp(request.user, 'event_liked', event)
                        if like_type == 'liked':
                            for voter in rating.voters.exclude(id=request.user.id):
                                award_xp(voter, 'rating_liked', event)
                        new_badges = check_badges(request.user)
                        queue_notification(request, xp_result, new_badges)

                    response = redirect('core:event', event_id=event_id)
                    response.set_cookie(f'liked_{event_id}', like_type, max_age=365*24*60*60)
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
            xp_result = award_xp(request.user, 'comment_posted', comment)
            new_badges = check_badges(request.user)
            queue_notification(request, xp_result, new_badges)

    return redirect('core:event', event_id=event.id)


@login_required
def reply_sent(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    event = comment.event

    if request.method == 'POST':
        form = CreateReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.comment = comment
            reply.author = request.user
            reply.save()
    
    return redirect('core:event', event_id=event.id)


@login_required
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    event = comment.event
    if request.user == comment.author:
        comment.delete()
    return redirect('core:event', event_id=event.id)


@login_required
def reply_delete(request, pk):
    reply = get_object_or_404(Reply, pk=pk)
    event = reply.comment.event
    if request.user == reply.author:
        reply.delete()
    return redirect('core:event', event_id=event.id)


@login_required
def comment_vote(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    comment = get_object_or_404(Comment, pk=pk)
    vote_type = request.POST.get('vote')

    if vote_type not in (CommentVote.LIKE, CommentVote.DISLIKE):
        return JsonResponse({'error': 'Invalid vote type'}, status=400)

    existing = CommentVote.objects.filter(user=request.user, comment=comment).first()

    if existing:
        if existing.vote == vote_type:
            existing.delete()
            user_vote = None
        else:
            existing.vote = vote_type
            existing.save()
            user_vote = vote_type
    else:
        CommentVote.objects.create(user=request.user, comment=comment, vote=vote_type)
        user_vote = vote_type

    # Award XP to the comment author when they receive a new like.
    # Only fires when a like lands (not on toggle-off, not when switching to dislike).
    if (
        user_vote == CommentVote.LIKE
        and comment.author
        and comment.author != request.user
    ):
        award_xp(comment.author, 'comment_liked', comment)
        check_badges(comment.author)

    likes = comment.votes.filter(vote=CommentVote.LIKE).count()
    dislikes = comment.votes.filter(vote=CommentVote.DISLIKE).count()

    return JsonResponse({'likes': likes, 'dislikes': dislikes, 'user_vote': user_vote})
