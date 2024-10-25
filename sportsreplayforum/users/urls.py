from django.urls import path, include
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm
from . import views


app_name = 'users'
urlpatterns = [
    path('register/', views.registration_view, name='register'),
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
]