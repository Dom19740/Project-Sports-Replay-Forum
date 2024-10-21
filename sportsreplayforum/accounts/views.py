from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, RegisterForm, UserUpdateForm, DeleteUserForm



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
