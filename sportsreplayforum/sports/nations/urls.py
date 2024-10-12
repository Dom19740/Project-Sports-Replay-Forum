from django.urls import path
from core import views

app_name = 'nations'
urlpatterns = [
    path('', views.competition_schedule, {'league': 'UEFA'}, name='competition_schedule'),
]
