from django.urls import path
from . import views

urlpatterns = [
    path('', views.race_list, name='race_list'), # F1 events list
    path('events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/rate/', views.rate_event, name='rate_event'),
    path('events/<int:event_id>/results/', views.event_results, name='event_results'),
]
