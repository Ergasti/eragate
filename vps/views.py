from vps.models import *
from django.shortcuts import render

def index(request):
	plans = Plan.objects.all()
	return render(request, 'main.html', {'plans': plans})