# Generated by Django 3.0.7 on 2020-12-31 10:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0040_remove_primary_enroll_logic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enroll',
            name='is_primary',
        ),
    ]
