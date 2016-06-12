from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

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
    

# Gives a form for patients to enter identifying data and be redirected to
# kiosk_data.
@login_required
def kiosk_home(request):
    pass

# Gives a form giving the patient a chance to update their info. Default
# values are obtained from the drchrono api
@login_required
def kiosk_data(request):
    pass

def about(request):
    return render(request, 'about.html')
