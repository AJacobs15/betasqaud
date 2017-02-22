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

def start():
    first_dict = C.crawl(100, starting_url, limiting_domain)
    final_dict = C.build_team_stats_dictionary(first_dict)
    bucks = first_dict['Milwaukee Bucks']
    sixers = first_dict['Philadelphia Sixers']

    new_bucks = []
    for player in bucks:
        name = []
        stats = []
        combined = []
        name.append(player[0])
        for stat in player[1]:
            stats.append(stat)
        combined = name + stats
        combined = tuple(combined)
        new_bucks.append(combined)
    bucks = pd.DataFrame(new_bucks)
    


    
    return bucks, sixers


team_avg = {}


