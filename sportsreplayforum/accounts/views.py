from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, RegisterForm


def sign_in(request):

    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('home')

        next_url = request.GET.get('next')
        form = LoginForm()
        return render(request,'accounts/login.html', {'form': form, 'next': next_url})
    
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request, user)
                messages.success(request,f'Hi {username.title()}, welcome back!')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('home')
        
        # If the form is not valid, log the error
        messages.error(request,f'Invalid username or password')
        return render(request,'accounts/login.html',{'form': form})
    

def sign_out(request):
    logout(request)
    next_url = request.GET.get('next')
    messages.success(request, 'You have logged out successfully.')
    if next_url:
        return redirect(next_url)
    else:
        return redirect('home')
    

def sign_up(request):
    next_url = request.GET.get('next')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            messages.success(request, 'You have registered and logged in successfully.')
            login(request, user)
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('home')
    else:
        next_url = request.GET.get('next')
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form, 'next': next_url})


