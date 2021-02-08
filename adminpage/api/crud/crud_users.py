from django.db import connection

from api.crud.utils import dictfetchall


def get_email_name_like_students(group_id: int, pattern: str, limit: int = 5):
    """
    Retrieve at most <limit students> which emails start with <email_pattern>
    @param pattern - beginning of student email/name
    @param limit - how many student will be retrieved maximum
    @return list of students that are
    """
    pattern = pattern.lower() + '%'
    with connection.cursor() as cursor:
        cursor.execute('SELECT '
                       'd.id AS id, '
                       'd.first_name AS first_name, '
                       'd.last_name AS last_name, '
                       'd.email AS email,'
                       'd.first_name || \' \' || d.last_name as full_name '
                       'FROM auth_user d, student s, "group" g '
                       'WHERE s.user_id = d.id '
                       'AND g.id = %(group_id)s '
                       'AND NULLIF('
                       '    sign(g.minimum_medical_group_id),'
                       '    (SELECT sign(medical_group_id) FROM student_medical_group, semester '
                       '     WHERE semester.id = semester_id '
                       '     AND semester_id <= g.semester_id '
                       '     AND student_id = s.user_id '
                       '     ORDER BY semester.start DESC '
                       '     LIMIT 1)'
                       ') is NULL '
                       'AND (d.email LIKE %(pattern)s OR '
                       'LOWER(d.first_name || \' \' || d.last_name) LIKE %(pattern)s OR '
                       'LOWER(d.last_name) LIKE %(pattern)s) '
                       'LIMIT %(limit)s',
                       {
                           "pattern": pattern,
                           "limit": str(limit),
                           "group_id": group_id
                       })
        return dictfetchall(cursor)
