from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm



class SignupForm(UserCreationForm):
    class Meta:
        model=CustomUser
        fields=['email','password1','password2','first_name','last_name']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email':'E-mail Id',
            'password1': 'Password',
            'password2':'Re-Enter Password'
        }