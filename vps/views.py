from vps.models import *
from django.shortcuts import render
from vps.forms import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.template import RequestContext
from django.contrib.auth import login as django_login
from django.contrib.auth import logout 
import random 
import string
import datetime
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from gbvp import settings

def index(request):
    plans = Plan.objects.all()
    return render(request, 'main.html', {'plans': plans})

next="/"
def login(request):
    global next
    if request.method == 'GET':
        next = request.GET['next'] 
        return render_to_response ('login.html',context_instance=RequestContext(request))
    if request.method == 'POST':
        print request.POST  
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        print user
        if user is not None:
            # the password verified for the user
            if user.is_active:
                django_login(request, user)
                print "User is valid, active and authenticated"
                return HttpResponseRedirect(next)
            else:
                return HttpResponse ("The password is valid, but the account has been disabled!")
        else:
            # the authentication system was unable to verify the username and password
            return HttpResponse ("The username and password were incorrect.")


def UserRegistration(request):
    if request.method == 'POST':
        data =  request.POST.copy()
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
                return HttpResponseRedirect('/')
        else:
            print form1.errors
            print form2.errors
            # form1 = UserCreateForm(prefix="form1")
            # form2 = RegistrationForm(prefix="form2")
            return render_to_response('register.html', {'form1': form1,'form2':form2}, context_instance=RequestContext(request))
    elif request.method == 'GET':

        form1 = UserCreateForm(prefix="form1")
        form2 = RegistrationForm(prefix="form2")
        return render_to_response('register.html', {'form1': form1,'form2':form2}, context_instance=RequestContext(request))

@login_required
def order(request):
    if request.method == 'GET':
        flavors = Flavor.objects.all()
        plans = Plan.objects.all()
        os_images=OSImage.objects.all()
        return render_to_response ('order.html',{'os_images':os_images,'plans': plans,'flavors':flavors},context_instance=RequestContext(request))
    if request.method == 'POST':
        order = Order(
            user = request.user, 
            plan = Plan.objects.get(pk=request.POST["plans"]), 
            subdomain=request.POST["subdomain"],
            os_image = OSImage.objects.get(pk=request.POST["os_image"]), 
            )
        order.save()
        return render_to_response ('order_confirm.html',{'order': order},context_instance=RequestContext(request))

@login_required
def order_withplan(request,plan):
    choosen = Plan.objects.get(pk=plan)
    flavors = Flavor.objects.all()
    plans = Plan.objects.all()
    os_images=OSImage.objects.all()
    return render_to_response ('order.html',{'os_images':os_images,'plans': plans,'flavors':flavors,'choosen':choosen},context_instance=RequestContext(request))

@login_required
def confirm_order(request):
    print request.POST
    order = Order.objects.get(pk=request.POST["order"])
    order.confirmed=True
    order.save();
    return HttpResponseRedirect('/dashboard/')

@login_required
def dashboard(request):
    vps = VPS.objects.filter(owner=request.user)
    return render_to_response ('dashboard.html',{'vps': vps},context_instance=RequestContext(request))

@login_required
def vps_action(request,action,vps):
    vps_obj = VPS.objects.get(pk=int(vps))
    if vps_obj.owner == request.user:
        if action == "status":
            vps_obj.get_instance_status()
        elif action == "reboot":
            vps_obj.reboot()
        elif action == "freboot":
            vps_obj.force_reboot_instance()
        elif action == "resume":
            vps_obj.resume_instance()
        elif action == "start":
            vps_obj.start_instance()
        elif action == "stop":
            print "diabled"
            # vps_obj.stop_instance()
        elif action =="vnc":
            try:
              url = vps_obj.generate_vnc_console_link()
              return mark_safe('<a class="btn btn-default" href="%s"><span class="glyphicon glyphicon-fullscreen"></span>View VPS</a>' % (url))
            except:
              return "VNC Not Available"
        elif action == "suspend":
            print "diabled"
            # vps_obj.suspend_instance()

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')

def switch_lang(request):
    if request.LANGUAGE_CODE == 'en': 
        request.session['django_language'] = 'ar'
    else:
        request.session['django_language'] = 'en'
    return HttpResponseRedirect('/')
