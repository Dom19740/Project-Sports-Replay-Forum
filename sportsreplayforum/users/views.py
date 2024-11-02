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
from .tokens import account_activation_token


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
            email.send()
            messages.success(request, 'Please check your email address to complete the registration')
            return redirect('home')
    return render(request, 'users/register.html', {'form': form})


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
                    return redirect(next_url)
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username/email or password.')

    else:
        form = CustomLoginForm()

    return render(request, 'home/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')

    return redirect('users:login')


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
