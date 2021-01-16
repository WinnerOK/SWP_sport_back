from admin_auto_filters.filters import AutocompleteFilter
from django.conf import settings
from django.contrib import admin
from django.db.models import F, Sum
from django.utils.html import format_html

from sport.models import SelfSportReport, Attendance
from .site import site
from .utils import custom_order_filter


class StudentTextFilter(AutocompleteFilter):
    title = "student"
    field_name = "student"


@admin.register(SelfSportReport, site=site)
class SelfSportAdmin(admin.ModelAdmin):
    list_display = (
        'student',
        'semester',
        'training_type',
        'link',
        'image',
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
        ("hours", "obtained_hours",),
        "link",
        "reference_image",
    )

    list_select_related = (
        'training_type',
    )

    readonly_fields = (
        "uploaded",
        "reference_image",
        "obtained_hours",
    )

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

    def reference_image(self, obj):
        if obj.image is not None:
            return format_html(
                '<a href="{}"><img style="width: 50%" src="{}" /></a>',
                obj.image.url,
                obj.image.url
            )
        else:
            return "None"

    reference_image.short_description = 'Reference'
    reference_image.allow_tags = True

    ordering = (F("approval").asc(nulls_first=True), "uploaded")

    class Media:
        pass
