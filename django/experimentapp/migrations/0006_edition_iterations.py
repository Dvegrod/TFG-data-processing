# Generated by Django 4.0.5 on 2022-06-16 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experimentapp', '0005_remove_aarm_edition_abstractrewardregister_edition_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='edition',
            name='iterations',
            field=models.IntegerField(default=0),
        ),
    ]
