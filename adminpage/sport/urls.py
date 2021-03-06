from django.urls import path, re_path
from django.contrib.auth.views import LoginView
from django.contrib.admin.views.decorators import staff_member_required

from .views import *

urlpatterns = [
    path('', LoginView.as_view(
        redirect_authenticated_user=True,
    ), name="login"),

    path('profile/', profile_view, name='profile'),
    path('category/', category_view, name='category'),
    path(
        'calendar/sport/<int:sport_id>',
        calendar_view,
        name="sport_schedule_calendar"
    ),
    path(
        'form/meg_group',
        process_med_group_form,
        name="process_med_group_form"
    ),
    re_path(
        r'dashboard/(?P<path>.*)$',
        staff_member_required(GraphanaProxyView.as_view()),
        name='grafana-dashboard'
    ),
]
