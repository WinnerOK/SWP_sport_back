# Generated by Django 3.0.7 on 2021-01-09 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0040_auto_20210109_1259'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='training',
            name='unique_training',
        ),
        migrations.AddField(
            model_name='training',
            name='custom_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
