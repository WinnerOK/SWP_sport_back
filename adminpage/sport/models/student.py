from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver

from sport.utils import get_current_study_year


class Student(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=False,
        limit_choices_to={
            'groups__verbose_name': settings.STUDENT_AUTH_GROUP_VERBOSE_NAME
        },
        primary_key=True,
    )

    is_ill = models.BooleanField(
        default=False,
    )

    medical_group = models.ForeignKey(
        'MedicalGroup',
        on_delete=models.DO_NOTHING,
        default=-2,
    )

    enrollment_year = models.PositiveSmallIntegerField(
        default=get_current_study_year,
    )

    telegram = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )

    def notify(self, subject, message, **kwargs):
        msg = message.format(**kwargs)
        send_mail(
            subject,
            msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
            html_message=msg.replace("\n", "<br>"),
        )

    def save(self, *args, **kwargs):
        if self.telegram is not None and self.telegram[0] != '@':
            self.telegram = '@' + self.telegram
        super().save(*args, **kwargs)

    class Meta:
        db_table = "student"
        verbose_name_plural = "students"

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} " \
               f"({self.user.email})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_student_profile(sender, instance, **kwargs):
    if Student.objects.filter(user=instance.pk).exists():
        instance.student.save()
