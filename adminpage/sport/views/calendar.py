from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from sport.models import Sport


@login_required
def calendar_view(request, sport_id, **kwargs):
    sport = get_object_or_404(Sport, pk=sport_id)
    return render(request, "calendar.html", {
        "sport": sport,
    })
