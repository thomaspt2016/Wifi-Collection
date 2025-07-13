from django import forms
from .models import CustomUser,Profile
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

class ProfileForm(forms.ModelForm):
    class Meta:
        model=Profile
        fields=['buildingid','phone','profpic','profile_comp']
        labels = {
            'profile_pic': 'Profile Picture', 
            'phone': 'Phone Number',          
            'buildingid':'Building ID',
            }