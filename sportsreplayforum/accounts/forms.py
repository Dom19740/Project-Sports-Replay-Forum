from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model


class RegisterForm(UserCreationForm):
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
        self.fields['username'].widget.attrs['placeholder'] = 'Username*'
        self.fields['email'].widget.attrs['placeholder'] = 'Email*'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password*'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password*'


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
    
    

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    error_messages = {
        'invalid_login': "Invalid credentials. Please check your username and password and try again.",
        'inactive': "This account is inactive.",
    }
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        # Remove labels by setting them to an empty string
        self.fields['username'].label = ''
        self.fields['password'].label = ''

        # Set placeholders
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['password'].widget.attrs['placeholder'] = 'Password'








class UserUpdateForm(UserChangeForm):
    password = None  # We don't want to display the password field here

    class Meta:
        model = User
        fields = ['username', 'email']  # Allow users to change only username and email

class DeleteUserForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Confirm account deletion")
