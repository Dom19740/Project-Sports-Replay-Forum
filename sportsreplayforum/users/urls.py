from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .forms import CustomPasswordResetForm, CustomPasswordResetConfirmForm
from . import views

app_name = 'users'
urlpatterns = [
    path('register/', views.registration_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset_form.html',
        form_class=CustomPasswordResetForm,
        email_template_name='users/password_reset_email.html',
        success_url=reverse_lazy('users:password_reset_done')
    ), name='password_reset'),

    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        form_class=CustomPasswordResetConfirmForm,
        success_url=reverse_lazy('users:password_reset_complete')
    ), name='password_reset_confirm'),

    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
]
