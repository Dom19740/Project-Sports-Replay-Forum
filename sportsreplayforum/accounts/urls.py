from django.urls import path
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm
from . import views


app_name = 'accounts'
urlpatterns = [
    path('register/', views.sign_up, name='register'),
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        
        form_class=CustomPasswordResetForm,
    ), name='password_reset'),
    path('password_reset_done/', auth_views. PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html',), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views. PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]