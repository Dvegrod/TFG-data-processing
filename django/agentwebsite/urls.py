"""agentwebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from experimentapp.views import *
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('domains', domains, name='domains'),
    path('domain/<int:domain_id>/subdomains', subdomains, name='subdomains'),
    path('subdomain/<int:subdomain_id>/editions', editions, name='editions'),
    path('edition/<int:edition_id>', edition_, name='edition'),
    path('aarm/<int:aarm_id>', aarm, name='aarm'),
    path('agents', agents, name='agents'),
    path('experiments', experiments, name='experiments'),
    path('new_agent', agent_creation, name='agent_creation'),
    path('new/agent', new_agent, name='new_agent'),
    path('new_experiment', experiment_creation, name='experiment_creation'),
    path('new/experiment', new_experiment, name='new_experiment'),
    path('experiment/<int:exp_id>', experiment, name='experiment_dash'),
    path('start/<int:exp_id>', START, name='experiment_start'),
]
