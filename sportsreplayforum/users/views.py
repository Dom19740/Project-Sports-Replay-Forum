from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import CustomRegisterForm, CustomLoginForm, UserUpdateForm, EmailUpdateForm, CustomPasswordChangeForm, DeleteAccountForm


def registration_view(response):

    next_url = response.GET.get('next')

    if response.method == "POST":
        form = CustomRegisterForm(response.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(response, f'Hi {user.username.title()}, you have registered and logged in successfully.')
            login(response, user)
            next_url = response.GET.get('next')

            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')
    else:
        next_url = response.GET.get('next')
        form = CustomRegisterForm()

    return render(response, "users/register.html", {'form': form, 'next': next_url})


def login_view(request):
    next_url = request.GET.get('next')

    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username.title()}!')

                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')

    else:
        form = CustomLoginForm()

    return render(request, 'users/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')

    return redirect('home')


@login_required
def profile_view(request):
    # Renders the profile page with all forms
    return render(request, 'users/profile.html', {
        'user_form': UserUpdateForm(instance=request.user),
        'email_form': EmailUpdateForm(instance=request.user),
        'password_form': CustomPasswordChangeForm(user=request.user),
        'delete_form': DeleteAccountForm()
    })

@login_required
def update_username(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Username updated successfully.')
            return redirect('users:profile')
    else:
        form = UserUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {'user_form': form})

@login_required
def update_email(request):
    if request.method == 'POST':
        form = EmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email updated successfully.')
            return redirect('users:profile')
    else:
        form = EmailUpdateForm(instance=request.user)
    return render(request, 'users/profile.html', {'email_form': form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keeps the user logged in
            messages.success(request, 'Password changed successfully.')
            return redirect('users:profile')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'users/profile.html', {'password_form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        form = DeleteAccountForm(request.POST)
        if form.is_valid() and form.cleaned_data.get('confirm'):
            request.user.delete()
            messages.success(request, 'Account deleted successfully.')
            return redirect('home')  # Redirect to home page after deletion
    else:
        form = DeleteAccountForm()
    return render(request, 'users/profile.html', {'delete_form': form})
