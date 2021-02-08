from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminDateWidget
from django.http import HttpRequest
from django.utils import timezone

from sport.models import (
    Attendance,
    Schedule,
    Enroll,
    Group,
    Training,
    StudentMedicalGroup,
)


class ViewMedicalGroupInline(admin.TabularInline):
    model = StudentMedicalGroup
    extra = 0
    ordering = ("-semester__start",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "semester",
            "medical_group"
        )


class ViewAttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0
    fields = ("training", "student", "hours")
    readonly_fields = ("training", "student")
    autocomplete_fields = ("training", "student")
    ordering = (
        "-training__start",
        "student__user__first_name",
        "student__user__last_name",
    )

    def has_add_permission(self, request, obj):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "training__group__semester",
            "student__user",
            "training__training_class"
        )


class AddAttendanceInline(ViewAttendanceInline):
    extra = 1
    verbose_name_plural = "Add extra attendance record"
    readonly_fields = ()

    def has_view_or_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return True


class HackAttendanceForm(forms.ModelForm):
    date = forms.DateField(
        label='Day',
        initial=timezone.now().date(),
        widget=AdminDateWidget(attrs={'size': 16})
    )

    class Meta:
        model = Attendance
        fields = ('hours',)


class HackAttendanceInline(ViewAttendanceInline):
    extra = 1
    verbose_name_plural = "Extra attendance records"
    readonly_fields = ()

    def has_view_or_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    form = HackAttendanceForm
    fields = ('date', 'hours',)


class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 0
    ordering = ("weekday", "start")
    autocomplete_fields = ("training_class",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "group__semester",
            "training_class",
        )


class EnrollInline(admin.TabularInline):
    model = Enroll
    extra = 0
    autocomplete_fields = ("student",)
    ordering = ("student__user__first_name", "student__user__last_name")

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "student__user",
            "group__semester",
        )


class GroupInline(admin.TabularInline):
    model = Group
    extra = 0
    ordering = ("semester", "name")


class TrainingInline(admin.TabularInline):
    model = Training
    fields = ("start", "end")
    extra = 0
    ordering = ("-start",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "group__semester",
            "training_class",
        )


class ViewTrainingInline(TrainingInline):
    exclude = ("group",)
    extra = 0

    def has_add_permission(
            self, request: HttpRequest, *args, **kwargs
    ) -> bool:
        return False
