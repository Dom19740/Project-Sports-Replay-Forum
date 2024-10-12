from django.urls import path
from core import views

app_name = 'f1'
urlpatterns = [
    path('', views.competition_schedule, {'league': 'Formula 1'}, name='competition_schedule'),
]
