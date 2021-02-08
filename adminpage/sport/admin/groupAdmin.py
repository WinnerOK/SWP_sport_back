from admin_auto_filters.filters import AutocompleteFilter
from django.conf import settings
from django.contrib import admin
from django.db.models.expressions import RawSQL

from api.crud import get_ongoing_semester
from sport.models import Group, MedicalGroup
from .inlines import ScheduleInline, EnrollInline, TrainingInline
from .utils import custom_titled_filter, has_free_places_filter
from .site import site


class TrainerTextFilter(AutocompleteFilter):
    title = "trainer"
    field_name = "trainer"


@admin.register(Group, site=site)
class GroupAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
    )

    autocomplete_fields = (
        "sport",
        "trainer",
    )

    list_filter = (
        ("semester", admin.RelatedOnlyFieldListFilter),
        has_free_places_filter(),
        ("is_club", custom_titled_filter("club status")),
        TrainerTextFilter,
        "minimum_medical_group",
        ("sport", admin.RelatedOnlyFieldListFilter),
    )

    list_display = (
        "__str__",
        "sport",
        "is_club",
        "trainer",
        "minimum_medical_group",
        "free_places",
    )

    inlines = (
        EnrollInline,
        ScheduleInline,
        TrainingInline,
    )

    list_select_related = (
        "semester",
        "sport",
        "trainer__user",
        "minimum_medical_group",
    )

    fields = (
        "name",
        "description",
        ("link_name", "link"),
        ("capacity", "free_places"),
        "is_club",
        "sport",
        "semester",
        "trainer",
        "minimum_medical_group",
    )

    readonly_fields = (
        "free_places",
    )

    def free_places(self, obj):
        return obj.capacity - obj.enroll_count

    # Dirty hack, filter autocomplete groups in "add extra form"
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if 'extra' in request.META.get('HTTP_REFERER', []):
            return qs.filter(semester=get_ongoing_semester(), sport__name=settings.OTHER_SPORT_NAME).order_by('name')
        return qs.annotate(enroll_count=RawSQL('select count(*) from enroll where group_id = "group".id', ()))

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "minimum_medical_group":
            kwargs["queryset"] = MedicalGroup.objects.filter(pk__gte=0)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    class Media:
        pass
