# Generated by Django 3.0.7 on 2021-02-06 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0054_migrate_medical_group'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='medical_group',
        ),
    ]
