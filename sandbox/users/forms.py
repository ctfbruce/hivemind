# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    """Form for registering new users."""
    email = forms.EmailField(required=True, help_text='Required. Enter a valid email address.')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {
            'username': None,
        }

class UserLoginForm(forms.Form):
    """Form for logging in existing users."""
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput, initial="test, remove this, this is to test recaptcha")


    recaptcha_token = forms.CharField(widget=forms.HiddenInput, required=False)
