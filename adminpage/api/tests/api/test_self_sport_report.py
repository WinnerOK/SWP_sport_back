import tempfile
from datetime import date

import pytest
from PIL import Image
from django.conf import settings
from django.db.models import Sum
from rest_framework import status
from rest_framework.test import APIClient

from api.views.self_sport_report import SelfSportErrors
from sport.models import SelfSportReport, SelfSportType, MedicalGroup, Attendance, Group, MedicalGroups

frozen_time = date(2020, 1, 2)
semester_start = date(2020, 1, 1)
semester_end = date(2020, 1, 15)


@pytest.fixture
@pytest.mark.freeze_time(frozen_time)
def setup(
        student_factory,
        semester_factory,
        student_medical_group_factory,
):
    email = "user@foo.bar"
    password = "pass"
    student = student_factory(
        email=email,
        password=password,
    )

    semester = semester_factory(
        name="S20",
        start=semester_start,
        end=semester_end,
    )
    selfsport_type, _ = SelfSportType.objects.get_or_create(
        name="self_sport",
        defaults={
            "application_rule": "just apply",
            "is_active": True,
        }
    )
    client = APIClient()
    client.login(
        email=email,
        password=password,
    )
    student_medical_group_factory(semester, student.student, MedicalGroups.GENERAL)
    return student, semester, selfsport_type, client


@pytest.mark.django_db
@pytest.mark.freeze_time(frozen_time)
def test_reference_upload_image(
        setup,
        freezer
):
    student, semester, selfsport_type, client = setup

    image_md = Image.new('RGB', (600, 600))
    file_md = tempfile.NamedTemporaryFile(suffix='.jpg')
    image_md.save(file_md)
    file_md.seek(0)

    response = client.post(
        f"/{settings.PREFIX}api/selfsport/upload",
        data={
            "image": file_md,
            "training_type": selfsport_type.pk,
        },
        format='multipart'
    )
    assert response.status_code == status.HTTP_200_OK
    assert SelfSportReport.objects.filter(
        semester=semester,
        student__pk=student.pk,
    ).count() == 1
    report = SelfSportReport.objects.filter(
        semester=semester,
        student__pk=student.pk,
    ).first()

    assert report.link is None
    assert report.image is not None


@pytest.mark.django_db
@pytest.mark.freeze_time(frozen_time)
def test_reference_upload_link(
        setup,
        freezer
):
    student, semester, selfsport_type, client = setup

    response = client.post(
        f"/{settings.PREFIX}api/selfsport/upload",
        data={
            "link": "http://example.com/",
            "training_type": selfsport_type.pk,
        },
        format='multipart'
    )

    assert response.status_code == status.HTTP_200_OK
    assert SelfSportReport.objects.filter(
        semester=semester,
        student__pk=student.pk,
    ).count() == 1
    report = SelfSportReport.objects.filter(
        semester=semester,
        student__pk=student.pk,
    ).first()

    assert report.link is not None
    assert report.image == ''


@pytest.mark.django_db
def test_reference_upload_medical_disalowance(
        setup,
        student_medical_group_factory,
):
    student, semester, selfsport_type, client = setup
    student_medical_group_factory(semester, student.student, MedicalGroups.NO_CHECKUP)

    response = client.post(
        f"/{settings.PREFIX}api/selfsport/upload",
        data={
            "link": "http://example.com/",
            "training_type": selfsport_type.pk,
        },
        format='multipart'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"] == SelfSportErrors.MEDICAL_DISALLOWANCE[0]


@pytest.mark.django_db
@pytest.mark.freeze_time(frozen_time)
def test_reference_upload_image_link(
        setup,
        freezer
):
    student, semester, selfsport_type, client = setup

    image_md = Image.new('RGB', (600, 600))
    file_md = tempfile.NamedTemporaryFile(suffix='.jpg')
    image_md.save(file_md)
    file_md.seek(0)

    response = client.post(
        f"/{settings.PREFIX}api/selfsport/upload",
        data={
            "image": file_md,
            "link": "https://google.com",
            "training_type": selfsport_type.pk,
        },
        format='multipart'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.freeze_time(frozen_time)
def test_reference_upload_image_invalid_size(
        setup,
        freezer
):
    student, semester, selfsport_type, client = setup

    image_sm = Image.new('RGB', (600, 300))
    image_lg = Image.new('RGB', (600, 5500))
    file_sm = tempfile.NamedTemporaryFile(suffix='.jpg')
    file_lg = tempfile.NamedTemporaryFile(suffix='.jpg')
    image_sm.save(file_sm)
    image_lg.save(file_lg)
    file_sm.seek(0)
    file_lg.seek(0)

    response = client.post(
        f"/{settings.PREFIX}api/selfsport/upload",
        data={
            "image": file_sm,
            "training_type": selfsport_type.pk,
        },
        format='multipart'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.post(
        f"/{settings.PREFIX}api/selfsport/upload",
        data={"image": file_lg, },
        format='multipart'
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@pytest.mark.freeze_time(frozen_time)
def test_self_sport_same_type_same_day(
        setup,
        freezer
):
    student, semester, selfsport_type, client = setup
    self_sport_group = Group.objects.get(
        semester=semester,
        name=settings.SELF_TRAINING_GROUP_NAME
    )
    report1 = SelfSportReport.objects.create(
        student_id=student.pk,
        semester=semester,
        link="https://example.com",
        training_type=selfsport_type
    )
    report1.save()
    report2 = SelfSportReport.objects.create(
        student_id=student.pk,
        semester=semester,
        link="https://example.ru",
        training_type=selfsport_type
    )
    report2.save()

    report1.hours = 5
    report1.save()

    report2.hours = 7
    report2.save()
    assert Attendance.objects.filter(
        student_id=student.pk,
        training__group=self_sport_group,
    ).aggregate(Sum("hours"))["hours__sum"] == report1.hours + report2.hours
