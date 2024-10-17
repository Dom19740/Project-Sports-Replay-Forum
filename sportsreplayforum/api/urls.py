from django.urls import path
from .views import get_sports, get_event_results

urlpatterns = [
    path('sports/', get_sports),
    path('events/<int:event_id>/results/', get_event_results),
]
