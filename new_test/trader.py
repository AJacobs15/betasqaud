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

def test_df():
    first_dict = C.crawl(100, starting_url, limiting_domain)
    final_dict = C.build_team_stats_dictionary(first_dict)
    team_names = list(first_dict.keys())
    teams = []

    for team in team_names:
        team = first_dict[team]
        roster = []
        for player in team:
            name = []
            stats = []
            name.append(player[0])
            for stat in player[1]:
                stats.append(stat)
            combined = tuple(name + stats)
            roster.append(combined)
        team = pd.DataFrame(roster, columns =['PLAYER', 'GP', 'MPG', 'FGM', 'FGA', 'FG%', '3PM', \
        '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'TOV', 'PF', 'OFR','DFR', 'RPG', 'APG', \
        'SPG', 'BPG', 'PPG'])
        teams.append(team)
    league = pd.concat(teams)

    
    return league, teams

league, teams = test_df()


def trade(team_a, targets):
        percents = ['3P%', 'FG%', 'FT%']
        flat =  ['RPG', 'APG', 'SPG', 'BPG', 'PPG']
        team_score = 0
        for i in range(len(team_a)):
            player = team_a.iloc[i]
            team_score += player_score(player, team_a)
        agents = []
        for i in range(len(targets)):
            agents.append((player_score(targets.iloc[i], team_a), targets.iloc[i]))
        agents.sort

        rank = 1
        print("Top Trade Targets")
        for player in agents:
            print(rank, player[1].loc["PLAYER"])
            feasibility(team_a, player[1])
            rank += 1


        return agents

def feasibility(team_a, target):

    team = []
    for i in range(len(team_a)):
        player = team_a.iloc[i]
        team.append((abs(stat_vector(target) - stat_vector(player)), player))
    team.sort()

    print("Likely trade chips for", target.loc["PLAYER"])
    rank = 1

    for tup in team:
        print(rank, tup[1].loc["PLAYER"])
        rank += 1

    return team


def stat_vector(player):

    stats = ['3P%', 'FG%', 'FT%','RPG', 'APG', 'SPG', 'BPG', 'PPG']
    vector = 0

    for stat in stats:
        l_avg = league[stat].mean()
        vector += (player.loc[stat] / l_avg)

    return vector


def player_score(player, team):
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

