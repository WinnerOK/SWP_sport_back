import csv
import io

from django.conf import settings
from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import AutocompleteSelectMultiple
from django.db import transaction
from django.http import HttpResponseRedirect
from django.utils import timezone

from api.crud import get_ongoing_semester
from sport.models import Training, Student, Attendance, Group
from .inlines import AttendanceInline
from .utils import cache_filter, cache_dependent_filter, cache_alternative_filter, custom_order_filter
from .site import site


class AutocompleteStudent:
    model = Student


class TrainingFormWithCSV(forms.Form):
    attended_students = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Student.objects.all(),
        widget=AutocompleteSelectMultiple(
            rel=AutocompleteStudent,
            admin_site=site,
            attrs={'data-width': '50%'}
        )
    )
    hours = forms.DecimalField(required=False, max_digits=5, decimal_places=2, min_value=0.01, max_value=999.99,
                               initial=1)
    csv = forms.FileField(required=False, widget=forms.FileInput(attrs={'accept': '.csv'}))

    def clean(self):
        cleaned_data = super().clean()
        attendances = []
        cleaned_data['attendances'] = attendances
        file = cleaned_data.get("csv", None)
        if file is None:
            return cleaned_data
        data = file.read().decode('UTF-8')
        for row in csv.reader(io.StringIO(data)):
            if len(row) != 2:
                raise forms.ValidationError(f"Expected 2 columns in each row, got {row}")
            student = Student.objects.filter(user__email=row[0]).first()
            if student is None:
                raise forms.ValidationError(f"Student with email {row[0]} not found")
            try:
                hours = float(row[1])
            except:
                raise forms.ValidationError(f"Cannot parse hours from {row[1]}")
            attendances.append((student, hours))

    @transaction.atomic
    def save(self, commit=True):
        training = super().save()
        if not commit:
            self.save_m2m = lambda: None
        for student in self.cleaned_data['attended_students']:
            Attendance.objects.update_or_create(student=student, training=training,
                                                defaults={'hours': self.cleaned_data['hours']})
        for (student, hours) in self.cleaned_data['attendances']:
            Attendance.objects.update_or_create(student=student, training=training, defaults={'hours': hours})
        return training


class ChangeTrainingForm(TrainingFormWithCSV, forms.ModelForm):
    class Meta:
        model = Training
        fields = ('group', 'schedule', 'start', 'end', 'training_class')


class CreateExtraTrainingForm(TrainingFormWithCSV, forms.ModelForm):
    class Meta:
        model = Training
        fields = ('group', 'start', 'end')


CreateExtraTrainingForm.title = "Add extra training"


@admin.register(Training, site=site)
class TrainingAdmin(admin.ModelAdmin):
    search_fields = (
        "group__name",
    )

    autocomplete_fields = (
        "group",
        "schedule",
        "training_class",
    )

    ordering = (
        '-start',
    )

    list_filter = (
        # semester filter, resets group sub filter
        (
            "group__semester",
            cache_filter(custom_order_filter(("-start",)), ["group__id"])
        ),
        # group filter, depends on chosen semester
        (
            "group",
            cache_dependent_filter({"group__semester": "semester"}, ("name",))
        ),
        ("training_class", admin.RelatedOnlyFieldListFilter),
        ("start", cache_alternative_filter(admin.DateFieldListFilter, ["group__semester"])),
    )

    list_display = (
        "group",
        # "schedule",
        "start",
        "end",
        "training_class",
    )

    inlines = (
        AttendanceInline,
    )

    fields = (
        "group",
        "schedule",
        "start",
        "end",
        "training_class",
    )

    def response_add(self, request, obj, post_url_continue=None):
        """Keep the same url on "Save and add one another"""
        res = super().response_add(request, obj, post_url_continue)
        if "_addanother" in request.POST:
            redirect_url = request.path + ('?extra=' if 'extra' in request.GET else '')
            return HttpResponseRedirect(redirect_url)
        else:
            return res

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Return custom form on ?extra= URL"""
        if obj is None and 'extra' in request.GET:
            kwargs['form'] = CreateExtraTrainingForm
        else:
            kwargs['form'] = ChangeTrainingForm
        return super().get_form(request, obj, change, **kwargs)

    def get_formsets_with_inlines(self, request, obj=None):
        """Skip inlines for custom form"""
        if obj is not None or 'extra' not in request.GET:
            yield from super().get_formsets_with_inlines(request, obj)

    def get_changeform_initial_data(self, request):
        """Custom form default values"""
        if 'extra' in request.GET:
            return {
                "group": Group.objects.get(semester=get_ongoing_semester(), name=settings.EXTRA_EVENTS_GROUP_NAME),
                "start": timezone.now().replace(minute=0, second=0),
                "end": timezone.now().replace(minute=30, second=0),
            }
        return {}

    def get_fieldsets(self, request, obj=None):
        return (
            (None, {
                'fields': ('group', 'start', 'end')
            }),
            ('Add attended students with same hours', {
                'fields': ('attended_students', 'hours',)
            }),
            ('Upload a csv file with attendance records', {
                'fields': ('csv',)
            }),
        )
