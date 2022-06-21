from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
import datetime
import requests

from .models import *

def dashboard(request):
    return render(request, 'experimentapp/dashboard.html')

def domains(request):
    ctx = {"domains" : Domain.objects,
           "e_select" : True if request.GET['e_select'] == 'true' else False}
    return render(request, 'experimentapp/w_domains.html', ctx)

def subdomains(request, domain_id):
    ctx = {"subdomains" : Subdomain.objects.filter(domain = domain_id),
           "domain" : Domain.objects.get(id=domain_id),
           "e_select" : True if request.GET['e_select'] == 'true' else False}
    return render(request, 'experimentapp/subdomains.html', ctx)

def editions(request, subdomain_id):
    ctx = {"editions" : Edition.objects.filter(sub_domain_id = subdomain_id),
           "e_select" : True if request.GET['e_select'] == 'true' else False}
    return render(request, 'experimentapp/editions.html', ctx)

def edition_(request, edition_id):
    edition_tuple = Edition.objects.get(id = edition_id)
    ctx = {"edition" : edition_tuple,
           "subdomain" : edition_tuple.sub_domain,
           "edition_aarms": AARM.objects.filter(sub_domain = edition_tuple.sub_domain)}
    return render(request, 'experimentapp/w_subdomain_edition.html', ctx)

def aarm(request, aarm_id):
    ctx = {"aarm" : AARM.objects.get(id = aarm_id)}
    return render(request, 'experimentapp/w_aarm.html', ctx)

def agents(request):
    agents = Agent.objects
    ctx = {"agents" : agents,
           "uses": Experiment.objects.raw('SELECT count(*) FROM public.experimentapp_experiment GROUP BY agent_id'),
           "a_select" : True if request.GET['a_select'] == 'true' else False}
    print(ctx['uses'])
    return render(request, 'experimentapp/w_agents.html', ctx)

def agent_creation(request):
    ctx = {"agents" : Agent.objects}
    return render(request, 'experimentapp/w_agent_create.html', ctx)

def new_agent(request):
    if request.method == 'POST':
        name = request.POST["name"]
        context = True if request.POST["ctx"] == 'true' else False
        fullref = True if request.POST["frf"] == 'true' else False
        Agent.objects.create(name=name,context=context,full_reinforce=fullref)
        return HttpResponse('')
    else:
        return HttpResponseBadRequest('Has to be POST')

def experiment_creation(request):
    return render(request, 'experimentapp/w_experiment_create.html')

def new_experiment(request):
    if request.method == 'POST':
        name = request.POST["name"]
        agent = request.POST["agent"]
        edition = request.POST["edition"]
        Experiment.objects.create(name=name,agent_id=agent,edition_id=edition,
                                  date_creation=datetime.datetime.now(),
                                  date_updated=datetime.datetime.now(),
                                  running=False,
                                  completed_iterations=0)
        return HttpResponse('')
    else:
        return HttpResponseBadRequest('Has to be POST')

def experiments(request):
    ctx = {"experiments" : Experiment.objects}
    return render(request, 'experimentapp/w_experiments.html', ctx)

def experiment(request, exp_id):
    ctx = {"experiment" : Experiment.objects.get(id=exp_id)}
    return render(request, 'experimentapp/w_experiment.html', ctx)

def START(request, exp_id):
    res = requests.get(f'http://localhost:8001/start/{exp_id}')
    return HttpResponse(res)
