# Generated by Django 4.0.5 on 2022-06-30 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experimentapp', '0008_episodeexecution_executionresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='executionresult',
            name='iteration',
            field=models.DateTimeField(),
        ),
    ]
