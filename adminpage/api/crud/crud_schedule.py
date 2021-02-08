from typing import Optional

from django.db import connection

from api.crud.utils import dictfetchall
from sport.models import Student


def get_sport_schedule(
        sport_id: int,
        student: Optional[Student] = None,
):
    """
    Retrieves existing schedules for the given sport type
    @param sport_id - searched sport id
    @param student - student, acquiring groups. Groups will be based on medical group
    @return list of trainings info
    """
    with connection.cursor() as cursor:
        cursor.execute('SELECT '
                       'g.id AS group_id, '
                       'g.name AS group_name, '
                       'count(e.id) AS current_load, '
                       'g.capacity AS capacity, '
                       's.weekday AS weekday, '
                       's.start AS start, '
                       's."end" AS "end", '
                       'tc.name AS training_class '
                       'FROM sport sp, "group" g LEFT JOIN enroll e ON e.group_id = g.id, schedule s '
                       'LEFT JOIN training_class tc ON s.training_class_id = tc.id '
                       'WHERE g.sport_id = sp.id '
                       'AND g.semester_id = current_semester() '
                       'AND s.group_id = g.id '
                       'AND sp.id = %(sport_id)s '
                       'AND NULLIF(sign(g.minimum_medical_group_id), sign(%(medical_group_id_sign)s)) is NULL '
                       'GROUP BY g.id, s.id, tc.id',
                       {
                           "sport_id": sport_id,
                           "medical_group_id_sign": 1 if student is None else student.medical_group_id
                       }
                       )
        return dictfetchall(cursor)
