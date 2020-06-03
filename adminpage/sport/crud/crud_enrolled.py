from sport.models import Student, Enroll, Group


def enroll_student_to_primary_group(group: Group, student: Student):
    """
    Enrolls given student in a primary group, removes all previous primary enrollments
    """
    Enroll.objects.filter(student=student, group__semester=group.semester).delete()
    Enroll.objects.create(student=student, group=group, is_primary=True)


def enroll_student_to_secondary_group(group: Group, student: Student):
    """
    Enrolls given student to a secondary group
    """
    Enroll.objects.create(student=student, group=group, is_primary=False)


def unenroll_student(group: Group, student: Student):
    """
    Unenrolls given student from a secondary group
    """
    Enroll.objects.filter(student=student, group=group, is_primary=False).delete()