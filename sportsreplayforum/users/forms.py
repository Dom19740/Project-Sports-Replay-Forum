from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm


class CustomRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Username field modifications
        self.fields['username'].label = ''
        self.fields['username'].help_text = ''
        self.fields['username'].widget.attrs['placeholder'] = 'Username'

        # Email field modifications
        self.fields['email'].label = ''
        self.fields['email'].required = True
        self.fields['email'].widget.attrs['placeholder'] = 'Email'

        # Password1 field modifications
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = ''
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'

        # Password2 field modifications
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = ''
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

    def clean_email(self):
        email = self.cleaned_data['email']
        if email and User.objects.filter(email=email).exists():
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
        'invalid_login': "Invalid credentials. Please check your username/email and password and try again.",
        'inactive': "This account is inactive.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Indicate that either username or email is accepted
        self.fields['username'].label = ''
        self.fields['username'].widget.attrs['placeholder'] = 'Username or Email'
        self.fields['password'].label = ''
        self.fields['password'].widget.attrs['placeholder'] = 'Password'


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Email field modifications
        self.fields['email'].label = ''
        self.fields['email'].widget.attrs['placeholder'] = 'Email'


class CustomPasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # New password 1 field modifications
        self.fields['new_password1'].label = ''
        self.fields['new_password1'].help_text = ''
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Password'

        # New password 2 field modifications
        self.fields['new_password2'].label = ''
        self.fields['new_password2'].help_text = ''
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = ''
        self.fields['username'].help_text = ''
        self.fields['username'].widget.attrs['placeholder'] = 'Username'


class EmailUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].label = ''
        self.fields['email'].help_text = ''
        self.fields['email'].widget.attrs['placeholder'] = 'email'


class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # New password 1 field modifications
        self.fields['new_password1'].help_text = ''

        # New password 2 field modifications
        self.fields['new_password2'].help_text = ''

        # Disable autofocus on old password field
        self.fields['old_password'].widget.attrs['autofocus'] = False



class DeleteAccountForm(forms.Form):
    confirm = forms.BooleanField(label="I confirm I want to delete my account", required=True)
