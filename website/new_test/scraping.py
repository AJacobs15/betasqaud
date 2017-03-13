import re
import utility as util
import bs4
import queue
import json
import sys
import csv
import numpy as np

url = "http://basketball.realgm.com/nba/teams/Boston-Celtics/2/Stats/2017/Averages"
url2 = "http://basketball.realgm.com/nba/teams/Chicago-Bulls/4/Stats/2017/Averages"

def get_data(soup, d):
    '''
    Function for grabbing all of the data for a team and storing it in a dictionary.
    Soup is a soup object created from bs4. The dictionary is the league dictionary, which 
    this function updates. 
    '''
    
    '''req1 = util.get_request(initial_url)
    text = util.read_request(req1)

    soup = bs4.BeautifulSoup(text, "html5lib")'''

    
    team_name = get_team_name(soup)
    if team_name not in d:
        d[team_name] = []
    
        tag_list = soup.find_all("td", class_ = 'nowrap')

        s = set()
        for tag in tag_list:

            player_name = tag.text
            #print(player_name)
            player_info = []
            t = tag.next_sibling
            for i in range(21):
                player_info.append(t.text)
                t = t.next_sibling
            player_info = player_info[1:]
            player_info = [float(x) for x in player_info]
            

            if player_name not in s:
                d[team_name].append((player_name, player_info))
                s.add(player_name)
            #print()
    return d


def get_team_name(soup):
    '''
    Uses regular expressions to grab the city and team name.
    Operates on a page in the gm stats website. Returns the team name.
    '''
    tag_list = soup.find_all("meta")
    tag_string = tag_list[1]["content"]

    
    word_list = re.findall('[A-Z]+[a-z]+ [A-Z]+[a-z]+', tag_string)
    team_name = word_list[0]
    return team_name











