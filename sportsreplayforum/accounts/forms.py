from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm

class LoginForm(forms.Form):
    username = forms.CharField(max_length=65)
    password = forms.CharField(max_length=65, widget=forms.PasswordInput)

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['email'].required = False
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email (optional)'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            self.add_error('username', 'Username already exists')
        return username

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



class UserUpdateForm(UserChangeForm):
    password = None  # We don't want to display the password field here

    class Meta:
        model = User
        fields = ['username', 'email']  # Allow users to change only username and email

class DeleteUserForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Confirm account deletion")
