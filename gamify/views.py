from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from core.models import Competition
from .leaderboards import (
    competition_leaderboard,
    global_alltime,
    global_period,
    sport_leaderboard,
)


def _limit(request, default=50, maximum=100):
    try:
        return min(int(request.GET.get('limit', default)), maximum)
    except (TypeError, ValueError):
        return default


def leaderboard_page(request):
    from core.views import sports as active_sports

    sport_boards = [
        {
            'name': s['name'],
            'title': s['title'],
            'slug': s['name'].lower().replace(' ', '-'),
            'results': sport_leaderboard(s['name'], 50),
        }
        for s in active_sports
    ]

    return render(request, 'gamify/leaderboard.html', {
        'alltime': global_alltime(50),
        'week': global_period('week', 50),
        'month': global_period('month', 50),
        'sport_boards': sport_boards,
    })


@require_GET
def leaderboard_alltime(request):
    return JsonResponse({
        'period': 'alltime',
        'results': global_alltime(_limit(request)),
    })


@require_GET
def leaderboard_week(request):
    return JsonResponse({
        'period': 'week',
        'results': global_period('week', _limit(request)),
    })


@require_GET
def leaderboard_month(request):
    return JsonResponse({
        'period': 'month',
        'results': global_period('month', _limit(request)),
    })


@require_GET
def leaderboard_sport(request, league):
    return JsonResponse({
        'league': league,
        'results': sport_leaderboard(league, _limit(request)),
    })


@require_GET
def leaderboard_competition(request, competition_id):
    competition = get_object_or_404(Competition, id=competition_id)
    return JsonResponse({
        'competition_id': competition_id,
        'competition_name': competition.name,
        'results': competition_leaderboard(competition_id, _limit(request)),
    })
