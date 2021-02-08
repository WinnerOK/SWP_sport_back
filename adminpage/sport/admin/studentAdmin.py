from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import ForeignKey
from django.db.models.expressions import RawSQL
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from import_export import resources, widgets, fields
from import_export.admin import ImportMixin
from import_export.results import RowResult

from api.crud import get_ongoing_semester
from sport.models import Student, MedicalGroup, StudentMedicalGroup, Semester
from sport.signals import get_or_create_student_group
from .inlines import (
    ViewAttendanceInline,
    AddAttendanceInline,
    ViewMedicalGroupInline,
)
from .site import site
from .utils import user__email


class MedicalGroupWidget(widgets.ForeignKeyWidget):
    def render(self, value: MedicalGroup, obj=None):
        return str(value)


class StudentResource(resources.ModelResource):
    medical_group = fields.Field(
        column_name="medical_group",
        attribute="medical_group",
        widget=MedicalGroupWidget(MedicalGroup, "pk"),
    )

    def get_or_init_instance(self, instance_loader, row):
        student_group = get_or_create_student_group()
        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            email=row["email"],
            defaults={
                "first_name": row.get("first_name"),
                "last_name": row.get("last_name"),
            },
        )

        student_model_fields = [
            f.name
            for f in Student._meta.fields
            if not isinstance(f, ForeignKey)
        ]

        student_import_fields = row.keys() & student_model_fields

        student, student_created = Student.objects.get_or_create(
            user=user,
            defaults=dict([
                (key, row[key])
                for key in student_import_fields
            ])
        )
        if student_created:
            user.groups.add(student_group)

        return student, student_created

    class Meta:
        model = Student
        fields = (
            "user",
            "user__email",
            "user__first_name",
            "user__last_name",
            "enrollment_year",
            "telegram",
        )
        export_order = (
            "user",
            "user__email",
            "user__first_name",
            "user__last_name",
            "medical_group",
            "enrollment_year",
            "telegram",
        )
        import_id_fields = ("user",)
        skip_unchanged = False
        report_skipped = True
        raise_errors = False

    def import_row(self, row, instance_loader, **kwargs):
        # overriding import_row to ignore errors
        # and skip rows that fail to import
        # without failing the entire import
        if not kwargs["dry_run"]:
            medical_group_id = row["medical_group"]
            del row["medical_group"]
            student, _ = self.get_or_init_instance(instance_loader, row)
            StudentMedicalGroup.objects.update_or_create(
                student=student,
                semester=get_ongoing_semester(),
                defaults={
                    "medical_group_id": medical_group_id
                }
            )

        import_result = super().import_row(row, instance_loader, **kwargs)
        if import_result.import_type == RowResult.IMPORT_TYPE_ERROR:
            # Copy the values to display in the preview report
            import_result.diff = [
                None,
                row.get('email'),
                row.get('first_name'),
                row.get('last_name'),
                row.get('medical_group'),
                row.get('enrollment_year'),
                row.get('telegram'),
            ]
            # Add a column with the error message
            import_result.diff.append(mark_safe(
                f'''Errors:<ul>{''.join([f'<li>{err.error}</li>' for err in import_result.errors])}</ul>'''
            ))
            # clear errors and mark the record to skip
            import_result.errors = []
            import_result.import_type = RowResult.IMPORT_TYPE_SKIP

        return import_result


@admin.register(Student, site=site)
class StudentAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = StudentResource

    def get_fields(self, request, obj=None):
        if obj is None:
            return (
                "user",
                "enrollment_year",
                "telegram",
            )
        return (
            "user",
            "is_ill",
            "medical_group_name",
            "enrollment_year",
            "telegram" if obj.telegram is None or len(obj.telegram) == 0 else ("telegram", "write_to_telegram"),
        )

    autocomplete_fields = (
        "user",
    )

    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "telegram",
    )

    list_filter = (
        "is_ill",
        "enrollment_year",
        #"medical_group",
    )

    list_display = (
        "__str__",
        user__email,
        "is_ill",
        "medical_group_name",
        "write_to_telegram",
    )

    readonly_fields = (
        "write_to_telegram",
        "medical_group_name",
    )


    def write_to_telegram(self, obj):
        return None if obj.telegram is None else \
            format_html(
                '<a target="_blank" href="https://t.me/{}">{}</a>',
                obj.telegram[1:],
                obj.telegram
            )

    ordering = (
        "user__first_name",
        "user__last_name"
    )

    inlines = (
        ViewMedicalGroupInline,
        AddAttendanceInline,
        ViewAttendanceInline,
    )

    list_select_related = (
        "user",
        #"medical_group",
    )

    def medical_group_name(self, obj):
        return obj.medical_group_name

    medical_group_name.short_description = 'Last medical group'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # TODO: show current primary group
        return qs.annotate(medical_group_name=RawSQL(
            'SELECT medical_group.name FROM medical_group, student_medical_group '
            'WHERE student_medical_group.student_id = student.user_id '
            'AND student_medical_group.semester_id = current_semester() '
            'AND medical_group.id = student_medical_group.medical_group_id',
            ()
        ))
