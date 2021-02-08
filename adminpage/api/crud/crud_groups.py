from typing import Optional

from django.conf import settings
from django.db import connection

import api.crud
from api.crud.utils import dictfetchall
from sport.models import Sport, Student, Trainer


def get_sports(all=False, student: Optional[Student] = None):
    """
    Retrieves existing sport types
    @param all - If true, returns also special sport types
    @param student - if student passed, get sports applicable for student
    @return list of all sport types
    """
    # w/o distinct returns a lot of duplicated
    if student is None or student.medical_group_id > 0:
        qs = Sport.objects.filter(group__minimum_medical_group_id__gt=0).distinct()
    elif student.medical_group_id < 0:
        qs = Sport.objects.filter(group__minimum_medical_group_id__lt=0).distinct()
    else:
        qs = Sport.objects.filter(group__minimum_medical_group_id=0).distinct()
    # Return those objects for which exists at least 1 group in current semester
    qs = qs.filter(group__semester__pk=api.crud.get_ongoing_semester().pk)
    return qs.all().values() if all else qs.filter(special=False).values()


def get_clubs(student: Optional[Student] = None):
    """
    Retrieves existing clubs
    @return list of all club
    """
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT '
            'g.id AS id, '
            'g.name AS name, '
            'sport.name AS sport_name, '
            's.name AS semester, '
            'capacity, description, trainer_id, is_club, '
            'count(e.id) AS current_load '
            'FROM sport, semester s, "group" g '
            'LEFT JOIN enroll e ON e.group_id = g.id '
            'WHERE s.id = current_semester() '
            'AND sport_id = sport.id '
            'AND semester_id = s.id '
            'AND is_club = TRUE '
            'AND NULLIF(sign(g.minimum_medical_group_id), sign(%(medical_group_id_sign)s)) is NULL '
            'GROUP BY g.id, sport.id, s.id', {
                "medical_group_id_sign": 1 if student is None else student.medical_group_id
            })
        return dictfetchall(cursor)


def get_student_groups(student: Student):
    """
    Retrieves groups, where student is enrolled
    @return list of group dicts
    """
    with connection.cursor() as cursor:
        cursor.execute('SELECT '
                       'g.id AS id, '
                       'g.name AS name, '
                       's.name AS sport_name '
                       'FROM enroll e, "group" g, sport s '
                       'WHERE g.semester_id = current_semester() '
                       'AND e.group_id = g.id '
                       'AND e.student_id = %s '
                       'AND s.id = g.sport_id ', (student.pk,))
        return dictfetchall(cursor)


def get_trainer_groups(trainer: Trainer):
    """
    For a given trainer return all groups he/she is training in current semester
    @return list of group trainer is trainings in current semester
    """
    with connection.cursor() as cursor:
        cursor.execute('SELECT '
                       'g.id AS id, '
                       'g.name AS name, '
                       's.name AS sport_name '
                       'FROM "group" g, sport s '
                       'WHERE g.semester_id = current_semester() '
                       'AND g.sport_id = s.id '
                       'AND g.trainer_id = %s', (trainer.pk,))
        return dictfetchall(cursor)


def get_sc_training_groups():
    """
    Finds sc training groups for the current semester
    @return list of group dict
    """
    with connection.cursor() as cursor:
        cursor.execute('SELECT '
                       'g.id AS id, '
                       'g.name AS name, '
                       's.name AS sport_name '
                       'FROM "group" g, sport s '
                       'WHERE g.semester_id = current_semester() '
                       'AND g.sport_id = s.id '
                       'AND g.name IN (%s, %s, %s) '
                       'ORDER BY g.name',
                       (settings.SC_TRAINERS_GROUP_NAME_FREE,
                        settings.SC_TRAINERS_GROUP_NAME_PAID,
                        settings.SELF_TRAINING_GROUP_NAME,
                        )
                       )
        row = dictfetchall(cursor)
    if row is None or len(row) != 3:
        raise ValueError("Unable to find SC training groups")
    return row
