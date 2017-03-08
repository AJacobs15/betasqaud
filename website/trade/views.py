from django.shortcuts import get_object_or_404,render
import json
from stats.models import Team

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
    team_traded = request.POST['Team']
    that_team = get_object_or_404(Team, pk=team_traded)
    possible_players = []
    stats = []
    stats.append((request.POST['GPmin'],request.POST['GPmax']))
    stats.append((request.POST['MPGmin'],request.POST['MPGmax']))
    stats.append((request.POST['FGMmin'],request.POST['FGMmax']))
    stats.append((request.POST['FGAmin'],request.POST['FGAmax']))
    stats.append((request.POST['FGmin'],request.POST['FGmax']))
    stats.append((request.POST['3PMmin'],request.POST['3PMmax']))
    stats.append((request.POST['3PAmin'],request.POST['3PAmax']))
    stats.append((request.POST['3Pmin'],request.POST['3Pmax']))
    stats.append((request.POST['FTMmin'],request.POST['FTMmax']))
    stats.append((request.POST['FTAmin'],request.POST['FTAmax']))
    stats.append((request.POST['FTmin'],request.POST['FTmax']))
    stats.append((request.POST['TOVmin'],request.POST['TOVmax']))
    stats.append((request.POST['PFmin'],request.POST['PFmax']))
    stats.append((request.POST['ORmin'],request.POST['ORmax']))
    stats.append((request.POST['DRmin'],request.POST['DRmax']))
    stats.append((request.POST['RPGmin'],request.POST['RPGmax']))
    stats.append((request.POST['APGmin'],request.POST['APGmax']))
    stats.append((request.POST['SPGmin'],request.POST['SPGmax']))
    stats.append((request.POST['BPGmin'],request.POST['BPGmax']))
    stats.append((request.POST['PPGmin'],request.POST['PPGmax']))
    with open('data_dump.json') as data_file:    
            data = json.load(data_file)
    for player in data:
        temp = data[player]['STATS']
        passes = True
        if data[player]['TEAM'] != team_traded:
            for stat in range(len(temp)):
                if temp[stat] >= int(stats[stat][0]):
                    if temp[stat] > int(stats[stat][1]):
                        passes = False
                else:
                    passes = False
        else:
            passes = False
        if passes:
            possible_players.append(player)
    return render(request, 'trade/results.html', {'possible_players': possible_players})