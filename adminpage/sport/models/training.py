from django.db import models
from django.db.models import Q, F
from django.forms.utils import to_current_timezone


class Training(models.Model):
    group = models.ForeignKey("Group", on_delete=models.SET_NULL, null=True)
    schedule = models.ForeignKey("Schedule", on_delete=models.SET_NULL, null=True, blank=True)
    start = models.DateTimeField(null=False)
    end = models.DateTimeField(null=False)
    training_class = models.ForeignKey("TrainingClass", on_delete=models.SET_NULL, null=True, blank=True)
    custom_name = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "training"
        verbose_name_plural = "trainings"
        constraints = [
            models.CheckConstraint(check=Q(start__lt=F('end')), name='training_start_before_end')
        ]
        indexes = [
            models.Index(fields=("group", "start")),
        ]

    def __str__(self):
        return f"{self.group} at {to_current_timezone(self.start).date()} " \
               f"{to_current_timezone(self.start).time().strftime('%H:%M')}-" \
               f"{to_current_timezone(self.end).time().strftime('%H:%M')}" \
               f"{'' if self.training_class is None else f' in {self.training_class}'}"

    @property
    def academic_duration(self) -> float:
        return round((self.end - self.start).total_seconds() / 2700, 2)
