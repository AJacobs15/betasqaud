from django.shortcuts import get_object_or_404,render

from .models import Team

def index(request):
    teams = Team.objects.all()
    team_list = []
    for team in teams:
        team_list.append(team)
    context = {'team_list': team_list}
    return render(request, 'stats/index.html', context)


def detail(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    return render(request, 'stats/detail.html', {'team':team})