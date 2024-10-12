from django.urls import path
from core import views

app_name = 'nations'
urlpatterns = [
    path('', views.competition_schedule, {'league': 'UEFA Nations League'}, name='competition_schedule'),
]
