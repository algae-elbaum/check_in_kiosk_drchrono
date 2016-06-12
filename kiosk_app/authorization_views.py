from django.shortcuts import render, redirect
import requests, datetime, pytz
from urllib import urlencode
from django.contrib.auth.decorators import login_required
from globs import client_id, client_secret, redirect_uri


def authorize(request):
    params = {'redirect_uri': redirect_uri,
              'response_type': 'code',
              'client_id': client_id,}
              # TODO isn't this how scope is supposed to work?
              #'scope': 'patients'}
    return redirect('https://drchrono.com/o/authorize/?' + urlencode(params))

@login_required
def authorization_redirect(request):
    # Check if the user denied permissions in authorization
    if 'error' in request.GET:
        return redirect('permissions_error')
    # This will raise an error on either the code key not existing or the 
    # code being invalid
    try:    
        # We have a valid code, use it to get our access token, refresh token
        # and authentication timeout
        response = requests.post('https://drchrono.com/o/token/', data={
                                 'code': request.GET['code'],
                                 'grant_type': 'authorization_code',
                                 'redirect_uri': redirect_uri,
                                 'client_id': client_id,
                                 'client_secret': client_secret})
        response.raise_for_status()
        data = response.json()
        # Fetch drchrono username
        response = requests.get('https://drchrono.com/api/users/current', headers={
                                'Authorization': 'Bearer %s' % data['access_token'],
                                 })
        response.raise_for_status()
        username = response.json()['username']

        doctor = request.user.doctor
        doctor.access_token = data['access_token']
        doctor.refresh_token = data['refresh_token']
        doctor.expires_timestamp = datetime.datetime.now(pytz.utc) \
                                    + datetime.timedelta(seconds=data['expires_in'])  
        doctor.username = username
        doctor.save()
        return redirect('home')
    except:
        return render(request, 'bad_authorization.html')


def permissions_error(request):
    return render(request, 'permissions_error.html')
