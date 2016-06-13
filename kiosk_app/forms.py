import django.forms as forms
from django.contrib.auth.models import User
from models import CheckIn

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class CheckInForm(forms.ModelForm):
    class Meta:
        model = CheckIn
        exclude = ['doctor',
                   'date_time',
                   'meds',
                   'allergies']
