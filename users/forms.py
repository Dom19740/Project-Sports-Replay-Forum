from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from core.models import Comment, Reply

class CustomRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = ''
        self.fields['username'].help_text = ''
        self.fields['username'].widget.attrs['placeholder'] = 'Username'

        self.fields['email'].label = ''
        self.fields['email'].required = True
        self.fields['email'].widget.attrs['placeholder'] = 'Email'

        self.fields['password1'].label = ''
        self.fields['password1'].help_text = ''
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'

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

        self.fields['username'].label = ''
        self.fields['username'].widget.attrs['placeholder'] = 'Username or Email'
        self.fields['password'].label = ''
        self.fields['password'].widget.attrs['placeholder'] = 'Password'


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].label = ''
        self.fields['email'].widget.attrs['placeholder'] = 'Email'


class CustomPasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['new_password1'].label = ''
        self.fields['new_password1'].help_text = ''
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Password'

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

        self.fields['new_password1'].help_text = ''

        self.fields['new_password2'].help_text = ''

        self.fields['old_password'].widget.attrs['autofocus'] = False


class DeleteAccountForm(forms.Form):
    confirm = forms.BooleanField(label="I confirm I want to delete my account", required=True)


class CreateCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class':'font1 text-4xl', 'rows': 2, 'placeholder': 'Add a comment...', 'style': 'width: 100%;'})
        }
        labels = {
            'body': ''
        }

class CreateReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class':'font1 text-4xl', 'rows': 2, 'placeholder': 'Add a reply...', 'style': 'width: 100%;'})
        }
        labels = {
            'body': ''
        }