from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from forms import CheckInForm

# This landing page for the site. User will be asked to log in through drchrono
# and then redirected to the home page
def landing(request):
    if request.user.is_authenticated():
        return redirect('home')
    # else:
    return render(request, 'landing.html')

# Gives links to enter kiosk mode or see the most recent check-ins
@login_required
def home(request):
    if not request.user.is_authenticated():
        return redirect('landing')
    return render(request, 'home.html')

# Gives a paginated list of check-ins, starting from the most recent 
@login_required
def get_check_ins(request):
    doctor = request.user.doctor
    check_in_list = doctor.check_in_set.order_by('date_time')
    paginator = Paginator(check_in_list, 25) # Show 25 per page
    page = request.GET.get('page')
    try:
        check_ins = paginator.page(page)
    except PageNotAnInteger:
        check_ins = paginator.page(1)
    except EmptyPage:
        check_ins = paginator.page(paginator.num_pages)
    return render(request, 'check_ins.html', {'check_ins': check_ins})
    
@login_required
def check_in_data(request):
    pass

# Gives a form for patients to enter identifying data and be redirected to
# kiosk_data.
@login_required
def kiosk_home(request):
    return render(request, 'kiosk_home.html')

# Gives a form giving the patient a chance to update their info. Default
# values are obtained from the drchrono api
@login_required
def kiosk_data(request):
    patient_data = request.user.doctor.get_patient_data(request.POST['firstname'],
                                                        request.POST['lastname'],
                                                        request.POST['ssn'])
    data_form = CheckInForm(initial=patient_data)
    if patient_data:
        context = {'data_form': data_form,
                   'meds': patient_data['meds'],
                   'allergies': patient_data['allergies']}
        return render(request, 'kiosk_data.html', context)
    else:
        return render(request, 'invalid_patient.html')

def about(request):
    return render(request, 'about.html')
