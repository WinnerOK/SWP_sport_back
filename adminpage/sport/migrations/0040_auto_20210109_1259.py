# Generated by Django 3.0.6 on 2021-01-09 12:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('sport', '0039_auto_20200830_1221'),
    ]

    operations = [
        migrations.RunSQL('''
ALTER TABLE training DROP CONSTRAINT same_date;
''')
    ]