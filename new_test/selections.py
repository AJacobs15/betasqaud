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
        if len(maximums) > 1:
            maximums = maximums[1:]
        if len(minimums) > 1:
            minimums = minimums[1:]
    players = []
    for player in original_file.index:
        players.append(player)
    
    return players