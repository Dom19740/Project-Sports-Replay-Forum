from django.urls import path
from .views import run_populate
from . import views

app_name = 'core'
urlpatterns = [
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('register/', views.sign_up, name='register'),
    path('competition_schedule/<str:league>/', views.competition_schedule, name='competition_schedule'),
    path('event_list/<int:competition_id>/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event, name='event'),
    path('events/<int:event_id>/vote/', views.vote, name='vote'),
    path('replay_platforms/', views.replay_platforms, name='replay_platforms'),
    path('search/', views.search, name='search'),
    path('run-f1-populate/', lambda request: run_populate(request, 'populate_f1', 'F1 data populated successfully'), name='run_populate_f1'),
    path('run-motogp-populate/', lambda request: run_populate(request, 'populate_motogp', 'MotoGP data populated successfully'), name='run_populate_motogp'),
    path('run-football-populate/', lambda request: run_populate(request, 'populate_football', 'Football data populated successfully'), name='run_populate_football'),
]