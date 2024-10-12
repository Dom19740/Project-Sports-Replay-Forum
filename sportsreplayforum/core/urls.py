from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('register/', views.sign_up, name='register'),
    path('competition_schedule/', views.competition_schedule, name='competition_schedule'),
    path('event_list/<int:competition_id>/', views.event_list, name='event_list'),
    path('events/<int:event_id>/vote/', views.vote, name='vote'),
]