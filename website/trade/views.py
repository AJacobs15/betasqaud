from django.shortcuts import get_object_or_404,render
import json
from stats.models import Team
from Cluster.final import *

def index(request):
    teams = Team.objects.all()
    team_list = []
    for team in teams:
        team_list.append(team)
    context = {'team_list': team_list}
    return render(request, 'trade/index.html', context)

def suggestions(request):
    teams = Team.objects.all()
    team_list = []
    for team in teams:
        team_list.append(team)
    team_traded = request.POST['TEAM']
    that_team = get_object_or_404(Team, pk=team_traded)
    possible_players = []
    min_stats = []
    max_stats = []
    min_stats.append(float(request.POST['GPmin']))
    max_stats.append(float(request.POST['GPmax']))
    min_stats.append(float(request.POST['MPGmin']))
    max_stats.append(float(request.POST['MPGmax']))
    min_stats.append(float(request.POST['FGMmin']))
    max_stats.append(float(request.POST['FGMmax']))
    min_stats.append(float(request.POST['FGAmin']))
    max_stats.append(float(request.POST['FGAmax']))
    min_stats.append(float(request.POST['FGmin']))
    max_stats.append(float(request.POST['FGmax']))
    min_stats.append(float(request.POST['3PMmin']))
    max_stats.append(float(request.POST['3PMmax']))
    min_stats.append(float(request.POST['3PAmin']))
    max_stats.append(float(request.POST['3PAmax']))
    min_stats.append(float(request.POST['3Pmin']))
    max_stats.append(float(request.POST['3Pmax']))
    min_stats.append(float(request.POST['FTMmin']))
    max_stats.append(float(request.POST['FTMmax']))
    min_stats.append(float(request.POST['FTAmin']))
    max_stats.append(float(request.POST['FTAmax']))
    min_stats.append(float(request.POST['FTmin']))
    max_stats.append(float(request.POST['FTmax']))
    min_stats.append(float(request.POST['TOVmin']))
    max_stats.append(float(request.POST['TOVmax']))
    min_stats.append(float(request.POST['PFmin']))
    max_stats.append(float(request.POST['PFmax']))
    min_stats.append(float(request.POST['ORmin']))
    max_stats.append(float(request.POST['ORmax']))
    min_stats.append(float(request.POST['DRmin']))
    max_stats.append(float(request.POST['DRmax']))
    min_stats.append(float(request.POST['RPGmin']))
    max_stats.append(float(request.POST['RPGmax']))
    min_stats.append(float(request.POST['APGmin']))
    max_stats.append(float(request.POST['APGmax']))
    min_stats.append(float(request.POST['SPGmin']))
    max_stats.append(float(request.POST['SPGmax']))
    min_stats.append(float(request.POST['BPGmin']))
    max_stats.append(float(request.POST['BPGmax']))
    min_stats.append(float(request.POST['PPGmin']))
    max_stats.append(float(request.POST['PPGmax']))
    categories = ['GP','MPG','FGM','FGA','FG%','3PM','3PA','3P%','FTM','FTA','FT%','TOV','PF','OFR','DFR','RPG','APG','SPG','BPG','PPG']
    Trading = GM(that_team.team_name, [categories,min_stats,max_stats])
    possible_players, temps = Trading.trader()

    return render(request, 'trade/results.html', {'possible_players': possible_players})