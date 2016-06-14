import django.forms as forms
from django.contrib.auth.models import User
from models import CheckIn

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class CheckInForm(forms.ModelForm):
    suffix = forms.CharField(required=False)
    middle_name = forms.CharField(required=False)
    nickname = forms.CharField(required=False)
    secondary_insurance_company = forms.CharField(required=False)
    secondary_insurance_ID = forms.CharField(required=False)
    secondary_insurance_group = forms.CharField(required=False)
    secondary_insurance_plan = forms.CharField(required=False)
    is_secondary_insurance_subscriber_the_same_as_the_patient =\
        forms.BooleanField(required=False)
    where_did_you_find_us = forms.CharField(required=False)
    what_specialists_do_you_see = forms.CharField(required=False)
    who_referred_you = forms.CharField(required=False)
    anything_special_we_need_to_know = forms.CharField(required=False)
    changes_to_medications = forms.CharField(required=False)
    changes_to_allergies = forms.CharField(required=False)
    questions_and_comments = forms.CharField(required=False)

    class Meta:
        model = CheckIn
        exclude = ['doctor',
                   'date_time',
                   'meds',
                   'allergies']
