import re
import utility as util
import bs4
import queue
import json
import sys
import csv


url = "http://basketball.realgm.com/nba/teams/Boston-Celtics/2/Stats/2017/Averages"
url2 = "http://basketball.realgm.com/nba/teams/Chicago-Bulls/4/Stats/2017/Averages"

def get_data(soup, d):
    '''
    function for grabbing all of the data for a team and storing it in a dictionary. 
    '''
    
    '''req1 = util.get_request(initial_url)
    text = util.read_request(req1)

    soup = bs4.BeautifulSoup(text, "html5lib")'''

    
    team_name = get_team_name(soup)

    if team_name not in d:
        d[team_name] = []
    
    tag_list = soup.find_all("td", class_ = 'nowrap')
    for tag in tag_list:

        player_name = tag.text
        player_info = []
        t = tag.next_sibling
        for i in range(21):
            player_info.append(t.text)
            t = t.next_sibling
        d[team_name] += [player_name, player_info]
    return d


def get_team_name(soup):
    '''
    Uses regular expressions to grab the city and team name.
    '''
    tag_list = soup.find_all("meta")
    tag_string = tag_list[1]["content"]

    
    word_list = re.findall('[A-Z]+[a-z]+ [A-Z]+[a-z]+', tag_string)
    team_name = word_list[0]
    return team_name


