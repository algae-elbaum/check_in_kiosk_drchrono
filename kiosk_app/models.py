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
   
    # Update the set of patients associated with this doctor
    def get_patient(self, first_name, last_name, ssn):
        headers={'Authorization': 'Bearer %s' % self.access_token}
        patients = []
        patients_url = 'https://drchrono.com/api/patients' + \
                       '?first_name=' + first_name + \
                       '?last_name=' + last_name
                        
        while patients_url:
            response = requests.get(patients_url, headers=headers)
            # This will tell us if the user needs to give us authorization
            response.raise_for_status()
            data = response.json()
            patients.extend(data['results'])
            patients_url = data['next'] # A JSON null on the last page
        
        # Filter the resulting patients on whether the ssn matches
        filtered = filter(lambda p: p['social_security_number'] == ssn,
                          patients)
        return filtered[0]

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


class Check_in(models.Model):
    # The longest name in the world is something like 225 characters. Let's 
    # allow some leeway
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, default=None)
    # datetime of check-in encoded as a string:
    date_time = models.CharField(max_length=50, default='')
    patient_name = models.CharField(max_length=50, default='')

    def __str__(self): 
        return self.patient_name + " check-in, " + str(self.date_time)

