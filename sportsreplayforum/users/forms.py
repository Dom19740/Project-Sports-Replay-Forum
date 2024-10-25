from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model


class CustomRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove labels by setting them to an empty string
        self.fields['username'].label = ''
        self.fields['email'].label = ''
        self.fields['password1'].label = ''
        self.fields['password2'].label = ''

        # Update help_text, placeholders, and other attributes
        self.fields['username'].help_text = ''
        self.fields['email'].required = True
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

        # Set placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'


    def clean_email(self):
        email = self.cleaned_data['email']
        if email:
            if User.objects.filter(email=email).exists():
                self.add_error('email', 'Email address already in use')
        return email

    def clean(self):
        cleaned_data = super().clean()
        if self.errors:
            self.fields['password1'].widget.attrs['value'] = self.data.get('password1')
            self.fields['password2'].widget.attrs['value'] = self.data.get('password2')
        return cleaned_data
    
    
class CustomLoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Invalid credentials. Please check your username and password and try again.",
        'inactive': "This account is inactive.",
    }
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)

        # Remove labels by setting them to an empty string
        self.fields['username'].label = ''
        self.fields['password'].label = ''

        # Set placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove labels by setting them to an empty string
        self.fields['email'].label = ''

        # Set placeholders
        self.fields['email'].widget.attrs['placeholder'] = 'Email'


class CustomPasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove labels by setting them to an empty string
        self.fields['new_password1'].label = ''
        self.fields['new_password2'].label = ''

        # Update help_text, placeholders, and other attributes
        self.fields['new_password1'].help_text = ''
        self.fields['new_password2'].help_text = ''

        # Set placeholders
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'