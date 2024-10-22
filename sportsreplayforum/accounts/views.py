from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import CustomRegisterForm, CustomLoginForm


def sign_up(response):

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

    return render(response, "accounts/register.html", {'form': form, 'next': next_url})


def sign_in(request):
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

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def sign_out(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')

    return redirect('home')