from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from forms import CheckInForm


# This landing page for the site. User will be asked to log in through drchrono
# and then redirected to the home page
def landing(request):
    if request.session.get('patient_mode'):
        return redirect('kiosk')
    if request.user.is_authenticated():
        return redirect('home')
    # else:
    return render(request, 'landing.html')

# Gives links to enter kiosk mode or see the most recent check-ins
@login_required
def home(request):
    if request.session.get('patient_mode'):
        return redirect('kiosk')
    if not request.user.is_authenticated():
        return redirect('landing')
    return render(request, 'home.html')

# Gives a paginated list of check-ins, starting from the most recent 
@login_required
def get_check_ins(request):
    if request.session.get('patient_mode'):
        return redirect('kiosk')
    doctor = request.user.doctor
    check_in_list = doctor.checkin_set.order_by('-date_time')
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
def check_in_data(request, id_str):
    if request.session.get('patient_mode'):
        return redirect('kiosk')
    doctor = request.user.doctor
    check_in = doctor.checkin_set.get(id=str(id_str))
    check_in_form = CheckInForm(instance=check_in)
    return render(request, 'check_in_data.html', {'check_in': check_in_form})

# Gives a form for patients to enter identifying data and be redirected to
# kiosk_data.
@login_required
def kiosk_home(request):
    request.session['patient_mode'] = True
    return render(request, 'kiosk_home.html')

# Gives a form giving the patient a chance to update their info. Default
# values are obtained from the drchrono api
@login_required
def kiosk_data(request):
    patient_data =\
        request.user.doctor.get_patient_data(request.POST['first_name'],
                                             request.POST['last_name'],
                                             request.POST['social_security_number'])
    # The patient will be sent back to this view if they filled in the form
    # incorrectly. In that case the request will have an old_form attribute
    # and we should use that as our form
    if hasattr(request, 'old_form'):
        data_form = request.old_form
    else:
        data_form = CheckInForm(initial=patient_data)
    if patient_data:
        context = {'data_form': data_form,
                   'meds': patient_data['meds'],
                   'allergies': patient_data['allergies']}
        return render(request, 'kiosk_data.html', context)
    else:
        return render(request, 'invalid_patient.html')

@login_required
def process_check_in(request):
    check_in_form = CheckInForm(request.POST)
    if check_in_form.is_valid():
        check_in = check_in_form.save(commit=False)
        check_in.doctor = request.user.doctor
        check_in.save()
        return render(request, 'kiosk_finish.html')
    else:
        request.old_form = check_in_form
        return kiosk_data(request)

def about(request):
    return render(request, 'about.html')
