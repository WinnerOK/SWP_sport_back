from admin_auto_filters.filters import AutocompleteFilter
from django import forms
from django.conf import settings
from django.contrib import admin
from django.db.models import F, Sum
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from sport.models import SelfSportReport, Attendance
from .site import site
from .utils import custom_order_filter


class StudentTextFilter(AutocompleteFilter):
    title = "student"
    field_name = "student"


class ReferenceAcceptRejectForm(forms.ModelForm):
    def clean_comment(self):
        if self.cleaned_data['hours'] == 0 and self.cleaned_data['comment'] == '':
            raise forms.ValidationError('Please, specify reject reason in the comment field')
        return self.cleaned_data['comment']

    class Meta:
        model = SelfSportReport
        fields = (
            "student",
            "semester",
            "training_type",
            "hours",
            "comment",
            "link",
        )


@admin.register(SelfSportReport, site=site)
class SelfSportAdmin(admin.ModelAdmin):
    form = ReferenceAcceptRejectForm

    list_display = (
        'student',
        'semester',
        'hours',
        'uploaded',
        'approval'
    )

    list_filter = (
        StudentTextFilter,
        ("semester", custom_order_filter(("-start",))),
        "approval"
    )

    fields = (
        "student",
        "semester",
        "training_type",
        "uploaded",
        ("hours", "obtained_hours", "medical_group", "comment"),
        "link",
        "reference_image",
        "attendance_link",
    )

    list_select_related = (
        'training_type',
    )

    readonly_fields = (
        "student",
        "uploaded",
        "reference_image",
        "obtained_hours",
        "attendance_link",
        "medical_group",
    )

    def attendance_link(self, obj):
        change_url = reverse('admin:sport_attendance_change', args=(obj.attendance.pk,))
        return mark_safe('<a href="%s">%s</a>' % (change_url, obj.attendance))

    attendance_link.short_description = 'Attendance'

    autocomplete_fields = (
        "student",
    )

    def obtained_hours(self, obj: SelfSportReport):
        return Attendance.objects.filter(
            student=obj.student,
            training__group__semester=obj.semester,
            training__group__name=settings.SELF_TRAINING_GROUP_NAME,
        ).aggregate(
            Sum('hours')
        )['hours__sum']

    obtained_hours.short_description = "Self sport hours in semester"

    def medical_group(self, obj: SelfSportReport):
        return obj.student.medical_group.name

    medical_group.short_description = "Student medical group"

    def reference_image(self, obj):
        if obj.image is not None:
            return format_html(
                '<a href="{}"><img style="width: 50%" src="{}" /></a>',
                obj.image.url,
                obj.image.url
            )
        else:
            return "None"

    def save_model(self, request, obj, form, change):
        if 'comment' in form.changed_data or \
                'hours' in form.changed_data or \
                'semester' in form.changed_data or \
                'training_type' in form.changed_data:
            super().save_model(request, obj, form, change)

    reference_image.short_description = 'Reference'
    reference_image.allow_tags = True

    ordering = (F("approval").asc(nulls_first=True), "uploaded")

    class Media:
        pass
