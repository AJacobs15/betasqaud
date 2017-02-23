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




for x in first_dict.keys():
    w_team = first_dict[x]
    w_stat = final_dict[x]
    team = []
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

    updated = []
    team_name = []
    new = []
    team_name.append(x)
    rest = w_stat[2:]
    time = w_stat[1]
    new_count = 0
    for t_stat in rest:
        rest[new_count] = t_stat/time
        new_count += 1
    new_combined = tuple(team_name + rest)
    new.append(new_combined)
    updated_team = pd.DataFrame(new)


    result = pd.concat([new_team, updated_team])
    result = result.reset_index(drop=True)