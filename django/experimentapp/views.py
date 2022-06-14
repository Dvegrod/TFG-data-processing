from django.shortcuts import render
from django.http import HttpResponse

from .models import *

def dashboard(request):
    return render(request, 'experimentapp/dashboard.html')

def domains(request):
    ctx = {"domains" : Domain.objects}
    return render(request, 'experimentapp/w_domains.html', ctx)

def subdomains(request, domain_id):
    ctx = {"subdomains" : Subdomain.objects.filter(domain = domain_id)}
    return render(request, 'experimentapp/subdomains.html')
