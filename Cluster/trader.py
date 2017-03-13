import re
import utility as util
import bs4
import queue
import json
import sys
import csv
import numpy as np
import pandas as pd
import scraping
import numpy as np
import julian_waugh_crawler as C

limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams" 



with open('return_dict.json') as data_file:    
    first_dict = json.load(data_file)


with open('roster_dict.json') as data_file:    
    roster_dict = json.load(data_file)




def test_df(roster_dict = None, first_dict = None, switch = True):    
    if not switch:
        first_dict, roster_dict = C.crawl(100, starting_url, limiting_domain)
    team_names = list(first_dict.keys())
    teams = []
    rosters = {}

    for teamname in team_names:
        team = first_dict[teamname]
        roster = []
        for player in team:
            name = []
            stats = []
            link = []
            name.append(player[0])
            for stat in player[1]:
                stats.append(stat)
            #print("team", teamname)
            #print("player", player[0])
            link.append(roster_dict[teamname][player[0]])
            combined = tuple(name + stats + link)
            roster.append(combined)

        team = pd.DataFrame(roster, columns =['PLAYER', 'GP', 'MPG', 'FGM', 'FGA', 'FG%', '3PM', \
        '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'TOV', 'PF', 'OFR','DFR', 'RPG', 'APG', \
        'SPG', 'BPG', 'PPG', 'LINK'])
        teams.append(team)
        rosters[teamname] = team
    league = pd.concat(teams)

    
    return league, rosters

#league, teams = test_df()


def trade(team_a, targets, league):
        percents = ['3P%', 'FG%', 'FT%']
        flat =  ['RPG', 'APG', 'SPG', 'BPG', 'PPG']
        team_score = 0
        for i in range(len(team_a)):
            player = team_a.iloc[i]
            team_score += player_score(player, team_a, league)
        agents = []
        for i in range(len(targets)):
            agents.append((player_score(targets.iloc[i], team_a, league), targets.iloc[i]))
        agents.sort

        rank = 1
        Top_Trade_Targets = []
        for player in agents:
            trade_chips = []
            trade_chips.append(rank)
            trade_chips.append(player[1].loc["PLAYER"])
            chips = feasibility(team_a, player[1], league)
            for chip in chips:
                trade_chips.append(chip)
            Top_Trade_Targets.append(trade_chips)
            rank += 1

    
        return Top_Trade_Targets #return agents

def feasibility(team_a, target, league):

    team = []
    for i in range(len(team_a)):
        player = team_a.iloc[i]
        team.append((abs(stat_vector(target, league) - stat_vector(player, league)), player))
    team.sort()

    #print("Likely trade chips for", target.loc["PLAYER"])
    rank = 1
    final_team = []
    for tup in team:
        final_team.append(rank)
        final_team.append(tup[1].loc["PLAYER"])
        #print(rank, tup[1].loc["PLAYER"])
        rank += 1
    return final_team


def stat_vector(player, league):

    stats = ['3P%', 'FG%', 'FT%','RPG', 'APG', 'SPG', 'BPG', 'PPG']
    vector = 0

    for stat in stats:
        l_avg = league[stat].mean()
        vector += (player.loc[stat] / l_avg)

    return vector


def player_score(player, team , league):
    percents = ['3P%', 'FG%', 'FT%']
    flat =  ['RPG', 'APG', 'SPG', 'BPG', 'PPG']
    total = 0
    for stat in flat:
        t_avg = team[stat].mean()
        l_avg = league[stat].mean()
        val = 0
        val = (player.loc[stat] / ((t_avg + l_avg) / 2)) * 5
        if val > 10:
            val = 10
        total += val
    for stat in percents:
        l_top = league[stat].quantile(.9)
        l_bot = league[stat].quantile(.1)
        t_top = team[stat].quantile(.9)
        t_bot = team[stat].quantile(.1)
        top = (l_top + t_top) / 2
        bot = (l_bot + t_bot) / 2
        t_avg = team[stat].mean()
        l_avg = league[stat].mean()
        avg = ((t_avg + l_avg) / 2)
        if player.loc[stat] == avg:
            val = 5
        elif player.loc[stat] > avg:
            val = ((player.loc[stat] - avg) / (top - avg)) * 5 + 5
            if val > 10:
                val = 10
        else:
            val = ((player.loc[stat] - avg) / (bot - avg)) * 5 
        total += val

    return total
    

def find_dataframe(first_dict):
    for x in first_dict.keys():
        w_team = first_dict[x]
        team = []
        list_mean = []
        list_mean.append(x)
        for pair in w_team:
            player = []
            player.append(pair[0])
            player = player
            minutes = pair[1][1]
            rest_of_stats = pair[1][2:]
            count = 0
            for stat in rest_of_stats:
                new_stat = stat/minutes
                rest_of_stats[count] = new_stat
                count += 1
            combined = tuple(player + rest_of_stats)
            team.append(combined)
        new_team = pd.DataFrame(team)
        mean = new_team.mean()
        for y in mean:
            list_mean.append(y)
        new_team.loc[len(new_team)] = list_mean
    return new_team

