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

class Edition(models.Model):
    id = models.AutoField(primary_key=True)
    sub_domain = models.ForeignKey(Subdomain, on_delete=models.CASCADE)
    name = models.CharField(max_length=64, default='Unnamed edition')
    iterations = models.IntegerField(default=0)
    interval = models.IntegerField()
    interweave = models.BooleanField(default=False)
    ignoregaps = models.BooleanField(default=False)

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
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE)
    date = models.DateField()
    enabled = models.BooleanField(default=False)
    reward = models.FloatField()

class Agent(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, default='Unnamed agent')
    context = models.BooleanField()
    full_reinforce = models.BooleanField()

class Experiment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128, default='Unnamed experiment')
    date_creation = models.DateTimeField()
    date_updated = models.DateTimeField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    edition = models.ForeignKey(Edition, on_delete=models.CASCADE)
    running = models.BooleanField()
    completed_iterations = models.IntegerField(default=0)

class EpisodeExecution(models.Model):
    id = models.AutoField(primary_key=True)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    date = models.DateTimeField()

class ExecutionResult(models.Model):
    id = models.BigAutoField(primary_key=True)
    episode = models.ForeignKey(EpisodeExecution, on_delete=models.CASCADE)
    iteration = models.DateTimeField()
    action = models.ForeignKey(AARM, on_delete=models.CASCADE)
    performance = models.FloatField()
    reward = models.FloatField()
