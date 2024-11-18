from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.about_view, name='about'),
    path('replay_platforms/', views.replay_platforms_view, name='replay_platforms'),
]
