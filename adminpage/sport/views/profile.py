from django import forms
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes

from api.crud import get_ongoing_semester, get_student_groups, \
    get_brief_hours, \
    get_trainer_groups
from api.permissions import IsStudent
from sport.models import Student, MedicalGroupReference
from sport.utils import set_session_notification


class MedicalGroupReferenceForm(forms.Form):
    reference = forms.ImageField()


def parse_group(group: dict) -> dict:
    return {
        "id": group["id"],
        'qualified_name': f'{group["name"]} ({group["sport_name"]})',
        "name": group["name"],
        "sport": group["sport_name"]
    }


@login_required
def profile_view(request, **kwargs):
    user = request.user

    student = Student.objects.filter(pk=user.pk).first()  # type: Optional[Student]
    trainer = getattr(user, "trainer", None)  # type: Optional[Trainer]

    current_semester = get_ongoing_semester()

    context = {
        "user": request.user,
        "common": {
            "semester_name": current_semester.name
        },
        "forms": {
            "medical_group_reference": MedicalGroupReferenceForm()
        },
    }

    if "notify" in request.session:
        msg_type, msg = request.session["notify"]
        context.update({
            "notify": {
                "msg": msg,
                "type": msg_type,
            }
        })
        del request.session["notify"]

    if student is not None:
        student_groups = get_student_groups(student)
        student_groups_parsed = list(map(
            parse_group,
            student_groups
        ))
        student_brief_hours_info = get_brief_hours(student)
        student_data = student.__dict__
        has_med_group_submission = MedicalGroupReference.objects.filter(
            student=student,
            semester=current_semester,
        ).exists()

        context.update({
            "student": {
                "student_id": student.pk,
                "sport_groups": student_groups_parsed,
                "group_choices_left": max(
                    0,
                    settings.STUDENT_MAXIMUM_GROUP_COUNT - len(
                        student_groups_parsed
                    )
                ),
                "semesters": student_brief_hours_info,
                "obj": student,
                "has_med_group_submission": has_med_group_submission,
                **student_data,
            },
        })

    if trainer is not None:
        training_groups = list(map(
            parse_group,
            get_trainer_groups(trainer)
        ))
        trainer_data = trainer.__dict__
        context.update({
            "trainer": {
                "sport_groups": training_groups,
                "obj": trainer,
                **trainer_data,
            },
        })

    return render(request, "profile.html", context)


@api_view(["POST"])
@permission_classes([IsStudent])
def process_med_group_form(request, *args, **kwargs):
    form = MedicalGroupReferenceForm(request.POST, request.FILES)
    if form.is_valid():
        MedicalGroupReference.objects.create(
            student_id=request.user.pk,
            semester=get_ongoing_semester(),
            image=form.cleaned_data["reference"],
        )

        set_session_notification(
            request,
            "Medical group reference successfully submitted",
            "success",
        )
        return redirect('profile')
    else:
        set_session_notification(request, "Form is invalid", "error")
    return redirect('profile')
