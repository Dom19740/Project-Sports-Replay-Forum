from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm

class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)

class RegisterForm(UserCreationForm):
    class Meta:
        model=User
        fields = ['username','email','password1','password2']
        labels = {
            'email': 'Email (optional)',
        }


class UserUpdateForm(UserChangeForm):
    password = None  # We don't want to display the password field here

    class Meta:
        model = User
        fields = ['username', 'email']  # Allow users to change only username and email

class DeleteUserForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Confirm account deletion")
