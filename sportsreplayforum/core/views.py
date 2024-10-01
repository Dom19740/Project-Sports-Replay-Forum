from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import LoginForm, RegisterForm


def sign_in(request):

    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('home')

        form = LoginForm()
        return render(request,'core/login.html', {'form': form})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}, welcome back!')
                return redirect('home')
        
        # form is not valid or user is not authenticated
        messages.error(request,f'Invalid username or password')
        return render(request,'core/login.html',{'form': form})
    

def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            messages.success(request, 'You have signed up successfully.')
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})


def sign_out(request):
    logout(request)
    messages.success(request,f'You have been logged out.')
    return redirect('home')