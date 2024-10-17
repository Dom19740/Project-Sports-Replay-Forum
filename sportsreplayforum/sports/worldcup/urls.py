from django.urls import path
from core import views

app_name = 'worldcup'
urlpatterns = [
    path('', views.competition_schedule, {'league': 'FIFA World Cup'}, name='competition_schedule'),
]
