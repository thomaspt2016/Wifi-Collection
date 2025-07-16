from django import forms
from .models import CustomUser,Profile,Building
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
    bulding = forms.ChoiceField(label='Building Name')
    floor = forms.ChoiceField(label='Floor Number')
    room = forms.ChoiceField(label='Room Number')

    class Meta:
        model = Profile
        fields = ['bulding', 'floor', 'room', 'phone', 'profpic']
        labels = {
            'profpic': 'Profile Picture',
            'phone': 'Phone Number',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bulding'].choices = list(Building.objects.values_list('building_name', 'building_name').distinct())
        self.fields['floor'].choices = list(Building.objects.values_list('floors', 'floors').distinct())
        self.fields['room'].choices = list(Building.objects.values_list('rooms', 'rooms').distinct())

        # Add an "empty" choice at the beginning (optional, but often good for dropdowns)
        self.fields['bulding'].choices.insert(0, ('', ' '))
        self.fields['floor'].choices.insert(0, ('', ' '))
        self.fields['room'].choices.insert(0, ('', ' '))