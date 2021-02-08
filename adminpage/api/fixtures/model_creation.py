from datetime import datetime, time, date
from typing import Optional

import pytest

from sport.models import (
    Attendance,
    Enroll,
    Group,
    Schedule,
    Semester,
    Sport,
    Student,
    StudentMedicalGroup,
    Trainer,
    Training,
    TrainingClass,
    MedicalGroups,
)


@pytest.fixture
@pytest.mark.django_db
def semester_factory():
    def create_semester(
            name: str,
            start: date,
            end: date,
    ) -> Semester:
        obj, _ = Semester.objects.get_or_create(
            name=name,
            defaults={
                "start": start,
                "end": end,
            }
        )
        return obj

    return create_semester


@pytest.fixture
@pytest.mark.django_db
def sport_factory():
    def create_sport(
            name: str,
            special: bool = False,
    ) -> Sport:
        obj, _ = Sport.objects.get_or_create(
            name=name,
            defaults={
                "special": special,
            }
        )
        return obj

    return create_sport


@pytest.fixture
@pytest.mark.django_db
def group_factory():
    def create_group(
            name: str,
            capacity: int,
            sport: Sport,
            semester: Semester,

            trainer: Optional[Trainer] = None,
            description: Optional[str] = None,
            is_club: bool = False,
            minimum_medical_group_id: MedicalGroups = MedicalGroups.PREPARATIVE,
    ) -> Group:
        obj, _ = Group.objects.get_or_create(
            name=name,
            semester=semester,
            defaults={
                "capacity": capacity,
                "sport": sport,
                "trainer": trainer,
                "description": description,
                "is_club": is_club,
                "minimum_medical_group_id": minimum_medical_group_id,
            }
        )
        return obj

    return create_group


@pytest.fixture
@pytest.mark.django_db
def schedule_factory():
    def create_schedule(
            group: Group,
            weekday: Schedule.Weekday,
            start: time,
            end: time,
            training_class: Optional[TrainingClass] = None,
    ) -> Schedule:
        obj, _ = Schedule.objects.get_or_create(
            group=group,
            weekday=weekday,
            start=start,
            end=end,
            defaults={
                "training_class": training_class,
            }
        )
        return obj

    return create_schedule


@pytest.fixture
@pytest.mark.django_db
def training_class_factory():
    def create_training_class(
            name: str
    ) -> TrainingClass:
        obj, _ = TrainingClass.objects.get_or_create(
            name=name,
        )
        return obj

    return create_training_class


@pytest.fixture
@pytest.mark.django_db
def training_factory():
    def create_training(
            group: Group,
            start: datetime,
            end: datetime,
            schedule: Optional[Schedule] = None,
            training_class: Optional[TrainingClass] = None
    ) -> Training:
        obj, _ = Training.objects.get_or_create(
            group=group,
            start=start,
            end=end,
            schedule=schedule,
            training_class=training_class,
        )
        return obj

    return create_training


@pytest.fixture
@pytest.mark.django_db
def enroll_factory():
    def create_enroll(
            student: Student,
            group: Group
    ):
        obj, _ = Enroll.objects.get_or_create(
            student=student,
            group=group
        )
        return obj

    return create_enroll


@pytest.fixture
@pytest.mark.django_db
def attendance_factory():
    def create_attendance(
            student: Student,
            training: Training,
            hours: float,
    ):
        obj, _ = Attendance.objects.get_or_create(
            student=student,
            training=training,
            hours=hours,
        )
        return obj

    return create_attendance


@pytest.fixture
@pytest.mark.django_db
def student_medical_group_factory():
    def create(
            semester: Semester,
            student: Student,
            medical_group_id: int,
    ):
        if hasattr(student, 'medical_group'):
            delattr(student, 'medical_group')
        obj, created = StudentMedicalGroup.objects.get_or_create(
            semester=semester,
            student=student,
            defaults={
                'medical_group_id': medical_group_id
            }
        )
        if not created:
            obj.medical_group_id = medical_group_id
            obj.save()
        return obj

    return create