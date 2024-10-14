from django.urls import path
from core import views

app_name = 'premier'
urlpatterns = [
    path('', views.competition_schedule, {'league': 'English Premier League'}, name='competition_schedule'),
]
