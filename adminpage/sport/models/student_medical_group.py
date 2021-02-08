from django.db import models


class StudentMedicalGroup(models.Model):
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    semester = models.ForeignKey("Semester", on_delete=models.CASCADE)
    medical_group = models.ForeignKey("MedicalGroup", on_delete=models.CASCADE)

    class Meta:
        db_table = "student_medical_group"
        verbose_name_plural = "student medical groups"
        unique_together = (("student", "semester"),)

    def __str__(self):
        return f"{self.student}: {self.medical_group}[{self.semester}]"
