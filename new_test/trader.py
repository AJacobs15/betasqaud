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

first_dict = C.crawl(100, starting_url, limiting_domain)
final_dict = C.build_team_stats_dictionary(first_dict)



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