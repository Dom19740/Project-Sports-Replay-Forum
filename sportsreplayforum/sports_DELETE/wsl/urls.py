from django.urls import path
from core import views

app_name = 'wsl'
urlpatterns = [
    path('', views.competition_schedule, {'league': 'English Womens Super League'}, name='competition_schedule'),
]
