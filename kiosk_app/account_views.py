from django.shortcuts import render, redirect
from django.contrib.auth.views import logout as django_logout
from django.contrib.auth.decorators import login_required
from models import Doctor
from forms import UserForm
from globs import redirect_uri


@login_required
def logout(request):
    # If the user was a properly logged in user with a username, remind them
    # that they may also want to log out from drchrono
    if hasattr(request.user, 'doctor') and request.user.doctor.username:
        username = request.user.doctor.username
        django_logout(request)
        return render(request, 'logout.html', {'username':username})
    # Otherwise just bring them home
    else:
        django_logout(request)
        return redirect('landing')

def register(request):
    # If there's a user logged in, require them to log out
    if request.user.is_authenticated():
        return redirect('manual_logout')
    # If it's post, the user has sent us their info and we need to try to set them up
    if request.method == 'POST':
        success = False
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            # Save the user and associate it with a new Doctor
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            doctor = Doctor()
            doctor.user = user
            doctor.save()
            success = True
            
        # Registration done, let's get out of here.
        # (note: I'm not actually sure whether it'd be more appropriate to
        # have a new view for the result and redirect to it. That sort of thing
        # seems common, but this seems simpler)
        return render(request, 'registration_report.html', {'success': success, 'user_form': user_form})

    # Otherwise we diplay the form for them to fill out and post to us
    else:
        return render(request, 'register.html', {'user_form': UserForm()}) 
       

@login_required
def manual_logout(request):
    return render(request, 'manual_logout.html')    


