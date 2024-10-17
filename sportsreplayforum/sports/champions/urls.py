from django.urls import path
from core import views

app_name = 'champions'
urlpatterns = [
    path('', views.competition_schedule, {'league': 'UEFA Champions League'}, name='competition_schedule'),
]
