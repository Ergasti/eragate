from vps.models import *
from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate


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