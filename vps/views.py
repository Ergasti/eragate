from vps.models import *
from django.shortcuts import render
from vps.forms import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext

import random 
import string
import datetime
from datetime import datetime, timedelta

def index(request):
	plans = Plan.objects.all()
	return render(request, 'main.html', {'plans': plans})


def login(request):
	print request.method 
	if request.method == 'GET':
	    return render_to_response ('login.html',context_instance=RequestContext(request))
	if request.method == 'POST':
		mail = request.POST['username']
		password = request.POST['password']
		user = authenticate(username='username', password='password')
		if user is not None:
		    # the password verified for the user
		    if user.is_active:
		        print("User is valid, active and authenticated")
		    else:
		        print("The password is valid, but the account has been disabled!")
		else:
		    # the authentication system was unable to verify the username and password
		    print("The username and password were incorrect.")

def UserRegistration(request):    
    if request.method == 'POST':
        data =  request.POST.copy()
        data['form1-username']=data['form1-email']
        print request.POST
        form1 = UserCreateForm(data, prefix="form1") 
        form2 = RegistrationForm(data, prefix="form2") 
        if form1.is_valid() and form2.is_valid(): 
                user = User(
                  username=form1.cleaned_data['username'],
                 is_active=True, email=form1.cleaned_data['email'], 
                 first_name=form1.cleaned_data['first_name'], 
                 last_name=form1.cleaned_data['last_name'])
                user.save()
                user.set_password(form1.cleaned_data['password1'])
                user.save()
                userprofile = UserProfile.objects.get(user=user)
                userprofile.gender=form2.cleaned_data['gender']
                userprofile.date_Of_birth=form2.cleaned_data['date_Of_birth']
                userprofile.phone_number=form2.cleaned_data['phone_number']
                userprofile.activation_key= ''.join(random.choice(string.ascii_uppercase + string.digits+ user.username) for x in range(10))
                userprofile.save()
                 # this creates the user
                # user.activation_key = ''.join(random.choice(string.ascii_uppercase + string.digits+ user.email) for x in range(20))
                created = datetime.now()
                print userprofile
                # title = "email verfication"
                # content = "http://127.0.0.1:8000/confirm_email/?vc=" + str(user.activation_key) 
                # send_mail(title, content, 'mai.zaied17@gmail.com.', [user.email], fail_silently=False)
                return HttpResponseRedirect('/thankyou/')
        else:
            print form1.errors
            form1 = UserCreateForm(prefix="form1")
            form2 = RegistrationForm(prefix="form2")
            return render_to_response('register.html', {'form1': form1,'form2':form2}, context_instance=RequestContext(request))
    elif request.method == 'GET':
        form1 = UserCreateForm(prefix="form1")
        form2 = RegistrationForm(prefix="form2")
        return render_to_response('register.html', {'form1': form1,'form2':form2}, context_instance=RequestContext(request))