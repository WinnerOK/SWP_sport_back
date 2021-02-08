from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin

from sport.models import StudentMedicalGroup
from .site import site


class StudentTextFilter(AutocompleteFilter):
    title = "student"
    field_name = "student"
    parameter_name = "student"


@admin.register(StudentMedicalGroup, site=site)
class StudentMedicalGroupAdmin(admin.ModelAdmin):
    list_filter = (
        StudentTextFilter,
        ("semester", admin.RelatedOnlyFieldListFilter),
    )

    list_display = (
        'student',
        'semester',
        'medical_group',
    )

    list_select_related = (
        "student",
        "student__user",
        "semester",
        "medical_group",
    )

    fields = (
        'student',
        'semester',
        'medical_group',
    )

    readonly_fields = (
        'student',
        'semester',
    )

    class Media:
        pass
