from django.urls import path
from . import views

app_name = 'gamify'

urlpatterns = [
    path('leaderboard/',                                      views.leaderboard_page,         name='leaderboard'),
    path('leaderboard/alltime/',                        views.leaderboard_alltime,      name='leaderboard-alltime'),
    path('leaderboard/week/',                           views.leaderboard_week,         name='leaderboard-week'),
    path('leaderboard/month/',                          views.leaderboard_month,        name='leaderboard-month'),
    path('leaderboard/sport/<str:league>/',             views.leaderboard_sport,        name='leaderboard-sport'),
    path('leaderboard/competition/<int:competition_id>/', views.leaderboard_competition, name='leaderboard-competition'),
]
