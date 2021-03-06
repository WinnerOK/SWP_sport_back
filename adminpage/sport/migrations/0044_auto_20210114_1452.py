# Generated by Django 3.0.7 on 2021-01-14 11:52

from django.db import migrations, models
import django.db.models.deletion
import image_optimizer.fields
import sport.models.self_sport


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0043_merge_20210113_1103'),
    ]

    operations = [
        migrations.CreateModel(
            name='SelfSportReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', image_optimizer.fields.OptimizedImageField(blank=True, null=True, upload_to=sport.models.self_sport.get_report_path)),
                ('link', models.URLField(blank=True, max_length=100, null=True)),
                ('hours', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('approval', models.BooleanField(null=True)),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sport.Semester')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sport.Student')),
            ],
            options={
                'db_table': 'self_sport_report',
            },
        ),
        migrations.AddConstraint(
            model_name='selfsportreport',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('link__isnull', True), models.Q(_negated=True, image__exact='')), models.Q(('image__exact', ''), ('link__isnull', False)), _connector='OR'), name='link_xor_image'),
        ),
    ]
