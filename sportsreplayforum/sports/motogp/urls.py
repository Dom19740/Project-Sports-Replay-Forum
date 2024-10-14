from django.urls import path
from core import views

app_name = 'motogp'
urlpatterns = [
    path('', views.competition_schedule, {'league': 'MotoGP'}, name='competition_schedule'),
]
