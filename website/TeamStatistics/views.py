from django.shortcuts import render

from .models import Team


def index(request):
    Teams = Team.objects.all()
    return render(request, 'TeamStatitistics/index.html', Teams)