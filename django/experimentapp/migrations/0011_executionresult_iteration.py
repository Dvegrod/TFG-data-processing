# Generated by Django 4.0.5 on 2022-06-30 10:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('experimentapp', '0010_remove_executionresult_iteration'),
    ]

    operations = [
        migrations.AddField(
            model_name='executionresult',
            name='iteration',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]