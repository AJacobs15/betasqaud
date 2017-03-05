import re
import utility as util
import bs4
import queue
import json
import sys
import csv
import scraping
import numpy as np
import pandas as pd


original_file = pd.read_csv("pure_stats.csv", delimiter='|')
original_file.columns = ['player', 'stat_num', 'stat']
original_file = original_file.pivot_table(index='player', columns='stat_num', values='stat')
original_file = original_file.fillna(value = 61.0)
original_file.columns = ['GS','Min', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', 'FTM', 'FTA', 'FT%', 'OFF', 'DEF', 'TRB', 'AST', 'STL', 'BLK', 'PF', 'TOV', 'PTS']

def selection(original_file, stat, minimum, maximum):
    '''
    Takes in a specific stat and a max or min. It returns and panda file 
    with the players that fall within this range.
    '''
    category = original_file[stat]
    original_file = original_file.loc[category > minimum]
    original_file = original_file.loc[category < maximum]

    return original_file

def ideal_players(original_file, categories, minimums, maximums):
    '''
    Takes in the users preferences for certain categories, returns a list
    of players that match all their preferences.
    '''
    for stat in categories:
        minimum = minimums[0]
        maximum = maximums[0]
        original_file = selection(original_file, stat, minimum, maximum)
        maximums = maximums[1:]
        minimums = minimums[1:]
    
    return original_file

def ideal_player_stats(original_file):
    players = []
    for player in original_file.index:
        player_stats = []
        player_stats.append(player)
        for column in original_file:
            player_file = original_file.loc[player]
            value = player_file.loc[column]
            player_stats.append(value)
        players.append(player_stats)
    
    return players

def just_players(original_file):
    players = []
    for player in original_file.index:
        players.append(player)

    return players


def test1(filename=original_file):
    categories = ["GS", 'FGA', 'FTM']
    minimums = [50, 13, 2]
    maximums = [59, 17, 5]
    players = ideal_players(filename, categories, minimums, maximums)

    return players

def test2(filename=original_file):
    categories = ["GS", 'FGA', 'FTM']
    minimums = [24, 1, 2]
    maximums = [59, 17, 3]

    players = ideal_players(filename, categories, minimums, maximums)

    return players