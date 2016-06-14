from django.conf.urls import url
from django.contrib.auth.views import login
from django.views.generic import RedirectView

import site_views, authorization_views, account_views

urlpatterns = [
    url(r'^$', site_views.landing, name='landing'),
    url(r'^home/', site_views.home, name='home'),
    url(r'^check_ins/([0-9]+)', site_views.check_in_data,
                                            name='check_in_data'),
    url(r'^check_ins/', site_views.get_check_ins, name='get_check_ins'),
    url(r'^kiosk/', site_views.kiosk_home, name='kiosk'),
    # kiosk doesn't look like a word anymore
    url(r'^kiosk_data/', site_views.kiosk_data, name='kiosk_data'),
    url(r'^process_check_in/', site_views.process_check_in, name='process_check_in'),
    url(r'^about/', site_views.about, name='about'),
   
    url(r'^authorize/', authorization_views.authorize, name='authorize'),
    url(r'^authorization_redirect/', authorization_views.authorization_redirect, name='authorization_redirect'),
    url(r'^permissions_error/', authorization_views.permissions_error, name='permissions_error'),

    url(r'^login/', login, {'template_name': 'login.html'}),
    url(r'^logout/', account_views.logout, name='logout'),
    url(r'^manual_logout/', account_views.manual_logout, name='manual_logout'),
    url(r'^register/', account_views.register, name='register'),
      
    # Not part of the project. I just want this url to still work while django is hogging port 80 
    url(r'^muse_server/$', RedirectView.as_view(url='http://gaster.caltech.edu:8000/muse_server/'))
]
