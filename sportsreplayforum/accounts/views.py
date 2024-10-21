from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, UserUpdateForm, DeleteUserForm, LoginForm


def sign_up(response):

    next_url = response.GET.get('next')

    if response.method == "POST":
        form = RegisterForm(response.POST)
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
        form = RegisterForm()

    return render(response, "accounts/register.html", {'form': form, 'next': next_url})


def sign_in(request):
    next_url = request.GET.get('next')

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
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
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})



""" def sign_in(response):
    next_url = response.GET.get('next')

    if response.method == "POST":
        form = AuthenticationForm(data=response.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(response, username=username, password=password)

            if user is not None:
                login(response, user)
                messages.success(response, f'Welcome back, {user.username.title()}! You are now logged in.')
                
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('home')
            else:
                messages.error(response, 'Invalid username or password.')
        else:
            messages.error(response, 'Please correct the errors below.')
    
    else:
        form = AuthenticationForm()

    return render(response, 'accounts/login.html', {'form': form, 'next': next_url})
     """

def sign_out(request):
    logout(request)
    next_url = request.GET.get('next')
    messages.success(request, 'You have logged out successfully.')
    if next_url:
        return redirect(next_url)
    else:
        return redirect('home')
    

# Create your views here

@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)
        delete_form = DeleteUserForm(request.POST)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('home')

        elif password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Prevents user from being logged out after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')

        elif delete_form.is_valid():
            user = request.user
            user.delete()
            messages.success(request, 'Your account has been deleted successfully!')
            return redirect('home')

    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)
        delete_form = DeleteUserForm()

    return render(request, 'accounts/profile.html', {
        'user_form': user_form,
        'password_form': password_form,
        'delete_form': delete_form,
    })
