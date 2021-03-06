# Generated by Django 3.0.7 on 2020-06-10 17:44

from django.db import migrations, models
import django.db.models.deletion
import sport.models.attendance


class Migration(migrations.Migration):

    dependencies = [
        ('sport', '0015_remove_old_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='capacity',
            field=models.PositiveIntegerField(default=50),
        ),
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='medical_references/')),
                ('hours', models.DecimalField(decimal_places=2, default=0, max_digits=3, validators=[sport.models.attendance.validate_hours])),
                ('uploaded', models.DateTimeField(auto_now_add=True)),
                ('semester', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sport.Semester')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sport.Student')),
            ],
            options={
                'verbose_name_plural': 'medical references',
                'db_table': 'reference',
            },
        ),
    ]
