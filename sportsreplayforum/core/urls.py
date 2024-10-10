from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('register/', views.sign_up, name='register'),
    path('competitions/<int:competition_id>/events/', views.event_list, name='event_list'),
    path('events/<int:event_id>/', views.event, name='event'),
    path('events/<int:event_id>/vote/', views.vote, name='vote'),
]