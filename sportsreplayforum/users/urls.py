from django.urls import path, include
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm
from . import views

app_name = 'users'
urlpatterns = [
    path('register/', views.registration_view, name='register'),
    path('login/', views.login_in_view, name='login'),
    path('logout/', views.logut_view, name='logout'),

    # Custom Password Reset Views
    path(
        'accounts/password_reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            form_class=CustomPasswordResetForm
        ),
        name='password_reset'
    ),
    path(
        'accounts/password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html'
        ),
        name='password_reset_confirm'
    ),
    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

    path('accounts/', include('django.contrib.auth.urls')),
]
