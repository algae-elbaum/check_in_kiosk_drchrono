import requests, datetime, pytz
from django.db import models
from django.contrib.auth.models import User
from globs import client_id, client_secret

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=50, default='')
    access_token = models.CharField(max_length=30, default='')
    refresh_token = models.CharField(max_length=30, default='')
    expires_timestamp = models.DateTimeField(default=datetime.datetime.now(pytz.utc))

    def __str__(self):
        return self.user.username  
  
    def get_data(self, data_url):
        ret = []
        headers={'Authorization': 'Bearer %s' % self.access_token}
        url = data_url
        while url:
            response = requests.get(url, headers=headers)
            # This will tell us if the user needs to give us authorization
            response.raise_for_status()
            data = response.json()
            ret.extend(data['results'])
            url = data['next'] # A JSON null on the last page
        return ret
        
    # Update the set of patients associated with this doctor
    def get_patient_data(self, first_name, last_name, ssn):
        patients_url = 'https://drchrono.com/api/patients' + \
                       '?first_name=' + first_name + \
                       '&last_name=' + last_name
        patients = self.get_data(patients_url)

        # Filter the resulting patients on whether the ssn matches
        ssn_to_int = lambda s: int(''.join(c for c in s if c.isdigit()))
        filtered = filter(lambda p: ssn_to_int(p['social_security_number']) == int(ssn),
                          patients)
        if (len(filtered) == 0):
            return None
        else:
            patient = filtered[0]
            # Copy insurance info to top level of patient dictionary
            # This loop seems to never run
            for ins in ['primary_insurance', 'secondary_insurance']:
                if ins in patient:
                    print 'got ' + ins
                    patient[ins + '_company'] =  patient[ins].insurance_company
                    patient[ins + '_ID'] = patient[ins].insurance_id_number
                    patient[ins + '_group'] = patient[ins].insurance_group_number
                    patient[ins + '_plan'] = patient[ins].insurance_plan_name
                    patient['is_' + ins + '_subscriber_the_same_as_the_patient'] =\
                                patient[ins].is_subscriber_the_patient
            
            # Retrieve medication and allergy info
            meds_url = 'https://drchrono.com/api/medications?patient=' +\
                       str(patient['id'])
            patient['meds'] = self.get_data(meds_url)
            allergies_url = 'https://drchrono.com/api/allergies?patient=' +\
                       str(patient['id'])
            patient['allergies'] = self.get_data(allergies_url)

            # Look for previous check-ins from this patient to get info that's
            # not visit specific. I don't know why the first three aren't
            # provided through the API endpoint
            keys_to_copy = ['nickname',
                            'suffix',
                            'work_phone',
                            'where_did_you_find_us',
                            'what_specialists_do_you_see',
                            'who_referred_you',
                            'do_you_use_online_scheduling',
                            'do_you_want_acess_to_online_portal']
            try:
                last_check_in =\
                    self.check_in_set.filter(social_security_number=ssn).latest('date_time')
                for k in keys_to_copy:
                    patients[k] = last_check_in[k]
            except:
                pass
            return patient

    # To prevent expiration and needing the user to reauthorize
    def refresh_authorization(self):
        response = requests.post('https://drchrono.com/o/token/', data={
                                 'refresh_token': self.refresh_token,
                                 'grant_type': 'refresh_token',
                                 'client_id': client_id,
                                 'client_secret': client_secret,
                                })
        response.raise_for_status()
        data = response.json()

        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.expires_timestamp = datetime.datetime.now(pytz.utc) \
                                    + datetime.timedelta(seconds=data['expires_in'])  
        doctor.save()


class CheckIn(models.Model):
    GENDER_CHOICES = [('', ''),
                      ('Female', 'Female'),
                      ('Male', 'Male'), 
                      ('Other', 'Other')]
    RACE_CHOICES = [('', ''),
                    ('indian', 'American Indian or Alaska Native'),
                    ('asian', 'Asian'),
                    ('black', 'Black or African American'),
                    ('hawaiian', 'Native Hawaiian or Other Pacific Islander'),
                    ('white', 'White'),
                    ('declined', 'Decline to specify')]
    ETH_CHOICES = [('', ''),
                   ('hispanic', 'Hispanic or Latino'),
                   ('not_hispanic', 'Not Hispanic or Latino'),
                   ('declined', 'Decline to specify')]
    LANGUAGE_CHOICES = [('', ''),
                        ('eng', 'English'),
                        ('zho', 'Chinese'),
                        ('fra', 'French'),
                        ('ita', 'Italian'),
                        ('jpn', 'Japanese'),
                        ('por', 'Portuguese'),
                        ('rus', 'Russian'),
                        ('spa', 'Spanish; Castilian'),
                        ('other', 'Other'),
                        ('unknown', 'Unknown'),
                        ('declined', 'Decline to specify')]
    STUDENT_CHOICES = [('', ''),
                       ('E', 'Employed'),
                       ('F', 'Full-time student'),
                       ('N', 'Not a Student'),
                       ('P', 'Part-time Student')]

    # The longest name in the world is something like 225 characters. Let's 
    # allow some leeway
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, default=None)
    date_time = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=256, default='')
    last_name = models.CharField(max_length=256, default='')
    middle_name = models.CharField(max_length=256, default='')
    suffix = models.CharField(max_length=50, default='')
    nickname = models.CharField(max_length=50, default='')
    gender = models.CharField(max_length=6, default='', choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    social_security_number = models.CharField(max_length=9, default='')
    race = models.CharField(max_length=12, default='', choices=RACE_CHOICES)
    ethnicity = models.CharField(max_length=11, default='',
                                 choices=ETH_CHOICES)
    preferred_language = models.CharField(max_length=20, default='',
                                          choices=LANGUAGE_CHOICES)
    home_phone = models.IntegerField()
    cell_phone = models.IntegerField()
    work_phone = models.IntegerField()
    email = models.CharField(max_length=50, default='')
    address = models.CharField(max_length=100, default='')
    zip_code = models.IntegerField()
    state = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=50, default='')
    emergency_contact_name = models.CharField(max_length=50, default='')
    emergency_contact_phone = models.IntegerField()
    emergency_contact_email = models.CharField(max_length=50, default='')
    emergency_contact_relation = models.CharField(max_length=50, default='')
    primary_insurance_company = models.CharField(max_length=100, default='')
    primary_insurance_ID = models.CharField(max_length=100, default='')
    primary_insurance_group = models.CharField(max_length=100, default='')
    primary_insurance_plan = models.CharField(max_length=100, default='')
    is_primary_insurance_subscriber_the_same_as_the_patient = models.BooleanField()
    secondary_insurance_company = models.CharField(max_length=100, default='')
    secondary_insurance_ID = models.CharField(max_length=100, default='')
    secondary_insurance_group = models.CharField(max_length=100, default='')
    secondary_insurance_plan = models.CharField(max_length=100, default='')
    is_secondary_insurance_subscriber_the_same_as_the_patient = models.BooleanField()
    patient_student_status = models.CharField(max_length = 10, default = '',
                                              choices=STUDENT_CHOICES)
    where_did_you_find_us = models.CharField(max_length=100, default='')
    what_specialists_do_you_see = models.TextField()
    who_referred_you = models.CharField(max_length=50, default='')
    do_you_use_online_scheduling = models.BooleanField()
    do_you_want_acess_to_online_portal = models.BooleanField()
    anything_special_we_need_to_know = models.TextField()
    meds = models.TextField()
    changes_to_medications = models.TextField()
    allergies = models.TextField()
    changes_to_allergies = models.TextField()

    reason_for_visit = models.TextField()
    questions_and_comments = models.TextField()
    have_you_read_the_provided_forms_and_consented = models.BooleanField()

    def __str__(self): 
        return self.patient_name + " check-in, " + str(self.date_time)


