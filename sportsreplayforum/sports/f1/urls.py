from django.urls import path
from . import views

urlpatterns = [
    path('', views.competition_schedule, name='competition_schedule'), # F1 events list
    path('competitions/<int:competition_id>/events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event, name='event'),
    path('events/<int:event_id>/vote/', views.vote, name='vote'),
]
