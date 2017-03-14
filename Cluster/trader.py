import re
import utility as util
import bs4
import queue
import json
import sys
import csv
import numpy as np
import pandas as pd
import scraping as s
import numpy as np
import julian_waugh_crawler as jw

limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams" 

def test_df(roster_dict = None, first_dict = None, switch = True): 
    """
    Call upon crawler to get necessary data for trading algorithm. Outputs two objects: league 
    and rosters. League is a dataframe of all the players in the NBA. Rosters is a dictionary 
    with keys equal to the name of NBA teams and values equal to a datafram with the stats of 
    the players of that particular team.

    If input "switch" is set to True, then test_df can skip crawling and convert two inputed
    dictionaries of stats, roster_dict and first_dict, into league and rosters. 
    """

    if not switch:
        first_dict, roster_dict = jw.crawl(100, starting_url, limiting_domain)
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


def trade(team_a, targets, league, roster_dict, team_name):
    '''
    Inputs:
        team_a - DataFrame of user's team
        targets - DataFrame of players that passed through the screener
        league - DataFrame of all the players in the NBA
        roster_dict - dictionary of DataFrames of all the teams in the NBA
        team_name - String of user's team name

    This function takes in DataFrames of the user's orginal team, players who have passed the screener,
    and players in the league and then runs them through various functions (each function will have a 
    its own more detailed explanation). Our trader assigns each possible trade target a player score that
    is calculated from individual player stats, team stats, and league stats. In addition, for each target
    player, this function generates a list of the players on the user's team roster that most closely 
    resembles the given target player based off similarities in statistical vectors. The function outputs a
    list of lists of two dataframes, one for the select target player, and one for the most similar players
    on the user's own team.

    '''
    percents = ['3P%', 'FG%', 'FT%']
    flat =  ['RPG', 'APG', 'SPG', 'BPG', 'PPG']
    team_score = 0
    for i in range(len(team_a)):
        player = team_a.iloc[i]
        team_score += player_score(player, team_a, league)
    agents = []
    for i in range(len(targets)):
        agents.append((player_score(targets.iloc[i], team_a, league), targets.iloc[i]))   
    agents = remove_team_agents(team_name, agents, roster_dict)
    agents.sort
    rank = 1
    Top_Trade_Targets = []
    count = 1
    for player in agents:
        if count <= 3:
            trade_chips = []
            #trade_chips.append(rank)
            trade_chips.append(player[1].loc["PLAYER"])
            count += 1
            chips = feasibility(team_a, player[1], league)
            count_1 = 1
            for chip in chips:
                if count_1 <= 3:
                    trade_chips.append(chip)
                    count_1 += 1
            Top_Trade_Targets.append(trade_chips)
            rank += 1
            
    return Top_Trade_Targets #return agents

def feasibility(team_a, target, league):
    """
    Inputs:
        team_a - DataFrame of user's team
        target - DataFrame of given target player 
        league - DataFrame of all players in NBA 

    This function creates a stat vector of the given target player based of his stats and 
    does the same for each player on team_a. It then outputs an ordered list of the players 
    on team_a in order of their promimity in stat vector value to the target player.

    """

    team = []
    for i in range(len(team_a)):
        player = team_a.iloc[i]
        team.append((abs(stat_vector(target, league) - stat_vector(player, league)), player))
    team.sort()
 
    output = []
    for tup in team:
        output.append(tup[1])
        
    team = output  

    return team
    
def remove_team_agents(team_name, agents, roster_dict):
    '''
    team_name is a string describing the team name.
    roster_dict is a nested dictionary mapping links to players and then players to teams.
    agents is a list of tuples of the form [(player_score, player_dataframe)...].

    '''
    dataframe_index = 1
    rv = []
   
    for agent in agents:
        name = agent[dataframe_index]['PLAYER']
        if name not in roster_dict[team_name]:
            rv.append(agent)
    return rv


def stat_vector(player, league):
    """
    inputs:
        player - player DataFrame
        league - NBA DataFrame
    Calculates a stat vector value that comes from normalized sums of given player's stats compared to league
    averages. Outputs a float value.
    """

    stats = ['3P%', 'FG%', 'FT%','RPG', 'APG', 'SPG', 'BPG', 'PPG']
    vector = 0
    for stat in stats:
        l_avg = league[stat].mean()
        vector += (player.loc[stat] / l_avg)

    return vector


def player_score(player, team , league):
    """
    Input:
        player - player DataFrame
        team - team DataFrame
        league - NBA DataFrame

    Calculates a player score for given player by assigning scores to each stat value for each player 
    based off of deviation from a weighted average of team and league averages for the stat. Outputs 
    a float value. 
    """

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
    """
    """

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

