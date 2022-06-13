from django.db import models

# Create your models here.

class Domain(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, default='Unnamed domain')
    description = models.CharField(max_length=1024, null=True)

class Subdomain(models.Model):
    id = models.AutoField(primary_key=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, default='Unnamed subdomain')
    description = models.CharField(max_length=1024, null=True)

class AARM(models.Model):
    id = models.BigAutoField(primary_key=True)
    sub_domain = models.ForeignKey(Subdomain, on_delete=models.CASCADE)
    name = models.CharField(max_length=128, default='Unnamed AARM')
    description = models.CharField(max_length=1024, null=True)

class RawArmDataRegister(models.Model):
    aarm = models.ForeignKey(AARM, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.FloatField()
    additional = models.JSONField(null=True)

class AbstractRewardRegister(models.Model):
    aarm = models.ForeignKey(AARM, on_delete=models.CASCADE)
    date = models.DateField()
    reward = models.FloatField()

class Experiment(models.Model):
    id = models.AutoField(primary_key=True)