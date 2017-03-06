from django.http import Http404

from django.shortcuts import render

from .models import Team

def index(request):
    teams = Team.objects.all()
    team_list = []
    for team in teams:
        team_list.append(team)
    context = {'team_list': team_list}
    return render(request, 'stats/index.html', context)


def detail(request, team_name):
    try:
        roster = Question.objects.get(pk=team_name)
    except Question.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'polls/detail.html', {'roster': roster})