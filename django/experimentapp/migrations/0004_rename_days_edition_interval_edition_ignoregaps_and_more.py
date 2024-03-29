# Generated by Django 4.0.5 on 2022-06-15 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experimentapp', '0003_agent_experiment_completed_iterations_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='edition',
            old_name='days',
            new_name='interval',
        ),
        migrations.AddField(
            model_name='edition',
            name='ignoregaps',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='edition',
            name='interweave',
            field=models.BooleanField(default=False),
        ),
    ]
