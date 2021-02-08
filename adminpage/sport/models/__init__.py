from django.contrib.auth.models import Group as DjangoGroup
from django.db import models

from .attendance import Attendance
from .enroll import Enroll
from .enums import MedicalGroups
from .group import Group
from .medical_group import MedicalGroup
from .medical_group_reference import MedicalGroupReference
from .reference import Reference
from .schedule import Schedule
from .self_sport import SelfSportReport
from .self_sport_type import SelfSportType
from .semester import Semester
from .sport import Sport
from .student import Student, save_student_profile
from .student_medical_group import StudentMedicalGroup
from .trainer import Trainer
from .training import Training
from .training_class import TrainingClass

DjangoGroup.add_to_class(
    'verbose_name',
    models.CharField(
        max_length=180,
        null=True, blank=False,
        unique=True,
    )
)

DjangoGroup.add_to_class(
    "__str__",
    lambda self: str(self.verbose_name)
)

DjangoGroup.add_to_class(
    "natural_key",
    lambda self: (str(self.verbose_name),)
)
