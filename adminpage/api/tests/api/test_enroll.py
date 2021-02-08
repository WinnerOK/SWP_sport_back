from datetime import date
from typing import Tuple

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from api.views.enroll import EnrollErrors
from sport.models import Enroll, Group, MedicalGroups, StudentMedicalGroup, Semester

User = get_user_model()

start = date(2020, 1, 1)
end = date(2020, 2, 20)


@pytest.fixture
def setup_group(
        semester_factory,
        sport_factory,
        group_factory,
) -> Group:
    sem = semester_factory(
        "S1",
        start,
        end,
    )

    sport = sport_factory("sport1", False)
    group = group_factory(
        "G1",
        capacity=1,
        sport=sport,
        semester=sem,
        trainer=None,
        is_club=True,
    )
    return group


@pytest.fixture
def logged_in_student(student_factory) -> Tuple[APIClient, User]:
    email = "user@foo.bar"
    password = "pass"
    student_user = student_factory(
        email=email,
        password=password,
    )
    student_user.save()
    client = APIClient()
    client.login(
        email=email,
        password=password,
    )
    return client, student_user


@pytest.mark.django_db
@pytest.mark.freeze_time('2020-01-01 10:00')
def test_enroll_one_success(
        setup_group: Group,
        logged_in_student,
        student_medical_group_factory,
):
    client, student_user = logged_in_student
    student_medical_group_factory(setup_group.semester, student_user.student, MedicalGroups.GENERAL)

    response = client.post(
        f"/{settings.PREFIX}api/enrollment/enroll",
        data={
            "group_id": setup_group.pk,
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert Enroll.objects.filter(
        student=student_user.student,
        group=setup_group,
    ).count() == 1

@pytest.mark.django_db
@pytest.mark.freeze_time('2021-01-01 10:00')
def test_enroll_lazy_medical_group(
        setup_group: Group,
        student_medical_group_factory,
        logged_in_student,
        semester_factory,
):
    client, student_user = logged_in_student
    semester_factory("S2", date(2021, 1, 1), date(2021, 2, 20))
    student_medical_group_factory(setup_group.semester, student_user.student, MedicalGroups.GENERAL)
    assert Semester.objects.count() == 2
    assert StudentMedicalGroup.objects.count() == 1

    response = client.post(
        f"/{settings.PREFIX}api/enrollment/enroll",
        data={
            "group_id": setup_group.pk,
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert Enroll.objects.filter(
        student=student_user.student,
        group=setup_group,
    ).count() == 1


@pytest.mark.django_db
@pytest.mark.freeze_time('2020-01-01 10:00')
def test_enroll_full_group(
        setup_group: Group,
        logged_in_student,
        student_medical_group_factory,
):
    client, student_user = logged_in_student
    student_medical_group_factory(setup_group.semester, student_user.student, MedicalGroups.GENERAL)

    setup_group.capacity = 0
    setup_group.save()
    response = client.post(
        f"/{settings.PREFIX}api/enrollment/enroll",
        data={
            "group_id": setup_group.pk,
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"] == EnrollErrors.GROUP_IS_FULL[0]
    assert Enroll.objects.filter(
        student=student_user.student,
    ).count() == 0


# TODO: maybe remove the test (just tests add to a group)
@pytest.mark.django_db
@pytest.mark.freeze_time('2020-01-01 10:00')
def test_enroll_two_success(
        setup_group: Group,
        logged_in_student,
        group_factory,
        student_medical_group_factory,
):
    client, student_user = logged_in_student
    student_medical_group_factory(setup_group.semester, student_user.student, MedicalGroups.GENERAL)

    response = client.post(
        f"/{settings.PREFIX}api/enrollment/enroll",
        data={
            "group_id": setup_group.pk,
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert Enroll.objects.filter(
        student=student_user.student,
        group=setup_group,
    ).exists()

    other_group = group_factory(
        "G2",
        capacity=1,
        sport=setup_group.sport,
        semester=setup_group.semester,
        trainer=setup_group.trainer,
        is_club=setup_group.is_club,
    )

    response = client.post(
        f"/{settings.PREFIX}api/enrollment/enroll",
        data={
            "group_id": other_group.pk,
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert Enroll.objects.filter(
        student=student_user.student,
        group=other_group,
    ).exists()


@pytest.mark.django_db
@pytest.mark.freeze_time('2020-01-01 10:00')
def test_enroll_insufficient_medical(
        setup_group: Group,
        logged_in_student,
        freezer,
        student_medical_group_factory,
):
    client, student_user = logged_in_student
    student_medical_group_factory(setup_group.semester, student_user.student, MedicalGroups.SPECIAL2)

    setup_group.minimum_medical_group_id = MedicalGroups.SPECIAL1
    setup_group.save()

    response = client.post(
        f"/{settings.PREFIX}api/enrollment/enroll",
        data={
            "group_id": setup_group.pk,
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"] == EnrollErrors.MEDICAL_DISALLOWANCE[0]


@pytest.mark.django_db
@pytest.mark.freeze_time('2020-01-01 10:00')
def test_enroll_too_many_groups(
        setup_group: Group,
        logged_in_student,
        group_factory,
        student_medical_group_factory
):
    client, student_user = logged_in_student
    student_medical_group_factory(setup_group.semester, student_user.student, MedicalGroups.GENERAL)
    groups = [setup_group]
    # setup group is G1, others are G2, G3 etc
    for i in range(2, settings.STUDENT_MAXIMUM_GROUP_COUNT + 2):
        g = group_factory(
            "G" + str(i),
            capacity=1,
            sport=setup_group.sport,
            semester=setup_group.semester,
            trainer=setup_group.trainer,
            is_club=setup_group.is_club,
        )
        groups.append(g)

    # enroll to max amount of groups
    for group in groups[:-1]:
        response = client.post(
            f"/{settings.PREFIX}api/enrollment/enroll",
            data={
                "group_id": group.pk,
            }
        )
        assert response.status_code == status.HTTP_200_OK

    response = client.post(
        f"/{settings.PREFIX}api/enrollment/enroll",
        data={
            "group_id": groups[-1].pk,
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["code"] == EnrollErrors.TOO_MUCH_GROUPS[0]
    assert Enroll.objects.filter(
        student=student_user.student,
    ).count() == settings.STUDENT_MAXIMUM_GROUP_COUNT


@pytest.mark.django_db
@pytest.mark.freeze_time('2020-01-01 10:00')
def test_unenroll_extra(
        setup_group: Group,
        logged_in_student,
        group_factory,
        enroll_factory,
        student_medical_group_factory,
):
    client, student_user = logged_in_student
    student_medical_group_factory(setup_group.semester, student_user.student, MedicalGroups.GENERAL)

    enroll_factory(
        student_user.student,
        setup_group,
    )

    g2 = group_factory(
        "G2",
        capacity=1,
        sport=setup_group.sport,
        semester=setup_group.semester,
        trainer=setup_group.trainer,
        is_club=setup_group.is_club,
    )

    enroll_factory(
        student_user.student,
        g2
    )
    response = client.post(
        f"/{settings.PREFIX}api/enrollment/unenroll",
        data={
            "group_id": g2.pk,
        }
    )

    assert response.status_code == status.HTTP_200_OK
    assert Enroll.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.freeze_time('2020-01-01 10:00')
def test_unenroll_only(
        setup_group: Group,
        logged_in_student,
        enroll_factory,
        student_medical_group_factory
):
    client, student_user = logged_in_student
    student_medical_group_factory(setup_group.semester, student_user.student, MedicalGroups.GENERAL)

    enroll_factory(
        student_user.student,
        setup_group,
    )

    response = client.post(
        f"/{settings.PREFIX}api/enrollment/unenroll",
        data={
            "group_id": setup_group.pk,
        }
    )

    assert response.status_code == status.HTTP_200_OK
    assert Enroll.objects.count() == 0
