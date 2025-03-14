from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .forms import CustomRegisterForm, CustomLoginForm, UserUpdateForm, EmailUpdateForm, CustomPasswordChangeForm, DeleteAccountForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login
from django.urls import reverse
from django.core.paginator import Paginator
from django.core.mail import BadHeaderError
from .tokens import account_activation_token
from core.models import Event
from core.views import sports


def registration_view(request):

    next_url = request.GET.get('next')
    form = CustomRegisterForm()

    if request.method == "POST":
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('users/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])

            try:
                email.send()
                
            except BadHeaderError:
                messages.error(request, 'Invalid header found.')
            except Exception as e:
                messages.error(request, f'An error occurred: your email is not valid. {e}')
                return render(request, 'users/register.html', {'form': form})
            return redirect('users:register_complete')
    return render(request, 'users/register.html', {'form': form})

def registration_complete(request):
    return render(request, 'users/register_complete.html')


def activate(request, uidb64, token):
    User = get_user_model()

    try:
        uid= force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, f'Hi {user.username.title()}. Your account has been successfully activated, you can login.')
        return redirect('users:login')

    else:
        messages.error(request, 'Activation link is invalid or expired')
        return redirect('home')
    

def login_view(request):
    next_url = request.GET.get('next')

    if request.method == "POST":
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            login_input = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=login_input, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username.title()}!')

                if next_url:
                    if next_url == reverse('users:login'):
                        return redirect('home')
                    else:
                        return redirect(next_url)
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username/email or password.')

    else:
        form = CustomLoginForm()

    return render(request, 'users/login.html', {
        'form': form, 'next': next_url
    })


def logout_view(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')

    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    rated_events = Event.objects.filter(rating__voters=user)

    paginator = Paginator(rated_events, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'user_form': UserUpdateForm(instance=user),
        'email_form': EmailUpdateForm(instance=user),
        'password_form': CustomPasswordChangeForm(user=user),
        'delete_form': DeleteAccountForm(),
        'page_obj': page_obj,
    }

    return render(request, 'users/profile.html', context)


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
            update_session_auth_hash(request, user)
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
            return redirect('home') 
    else:
        form = DeleteAccountForm()
    return render(request, 'users/profile.html', {'delete_form': form})
