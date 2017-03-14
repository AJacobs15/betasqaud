import re
from Crawler.utility import *
import bs4
import queue
import json
import sys
import csv
from .scraping import *
import numpy as np


'''
READ FOR GENERAL information

This file is where where we scrape and clean the data. The important function is crawl. It is an updated 
crawler function from pa2 that works on the real GM website. I return a statistics dictionary and a roster dictionary
that contains qualitative data (bio, awards, images etc)


The only major cleaning that I had to do was eliminating players who showed up on multiple teams (were traded) and eliminating
players who were waived. This was easy once I realized that although the statistics pages are not regularly updated, the 
roster pages are.


'''









limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams"


bad_link = 'http://basketball.realgm.com/nba/stats'


def generate_links(soup, proper_url, limiting_domain):
    '''
    Takes a url as input. Returns the urls of all of the pages linked 
    to the initial page in list format. Note that for the final version 
    that does not only crawl the web, we will also want to get information
    off of these web pages.
    '''
    #reach out to web page
    
    links_list = soup.find_all("a", string = "Stats")

    #find links
    rv = []
    s = set()
    for link in links_list:
        url = link.get('href')
        new_url = remove_fragment(url)

        converted_url = convert_if_relative_url(proper_url, new_url)


        converted_url = str(converted_url)
        if converted_url != None:
            if is_url_ok_to_follow(converted_url, limiting_domain):
                if converted_url not in s:

                    s.add(converted_url)
                    rv.append(converted_url)
    return rv


    

def list_to_queue(list_, q=queue.Queue()):
    '''
    Very simple helper function used at the beginning of crawl 
    to put all of the starting links into the initial queue.
    '''
    for term in list_:
        q.put(term)
    return q

def get_next_link(set_, queue):
    '''
    Check if the link has already been in the queue.
    input: set_ is a set consiting of visited links.
    queue is a queue consiting of links to visit.

    returns: queue is the updated queue, next_in_queue is the
    next link(if it exists), and a boolean indicating whether or not
    a next link can be returned.
    '''
    if queue.empty():
            return queue, None, False
    else:
            
        next_in_queue = queue.get()
        while next_in_queue in set_:
            if not queue.empty():
                next_in_queue = queue.get()
            else:
                return queue, None, False
    return queue, next_in_queue, True






def turn_starting_links_to_roster_dictionary(starting_links, limiting_domain):
    '''
    I am not crawling again. Instead, I will leverage symmetry in website urls.
    Returns a dictionary that maps team name to players and their respective player page links.

    Basically, when I origianally crawl for stats, I am easily able to capture all of the links
    of the stats pages. But for some reason, it is a lot harder to get links for the 
    roster pages. Thus, when I run this function, instead of crawling, I just notice
    that the links are super similar and I build all of the links that I need.


    '''
    add_string = 'Rosters/Regular/2017'
    l = 'http://basketball.realgm.com/nba/stats'
    bad_index = -19


    rv = {}
    for link in list(set(starting_links)):
        if link != l:
           link = link[: bad_index] + add_string
           name = get_team_name(link)
           player_d = build_real_roster(link, limiting_domain)
           rv[name] = player_d
    return rv           





def check_roster_size(roster_d):
    '''
    Simple function for test purposes. Loops over all of the teams in the 
    league dictionary. Delete before submitting because we do not want them 
    to see that some teams are too long.
    '''
    for k, v in roster_d.items():
        print(k, len(v))



def get_team_name(string):
    '''
    string is a url. Captures the team name for that url.
    Then, returns it as a string without any dashes.

    '''
    first_index = 6
    name = re.findall('teams/[A-Za-z-]+', string)[0]
    rv = name[first_index:].replace('-', ' ')
    return rv


def first_last_name(string):
    '''
    All of the player's names appear on the page in lastname, firstname order.
    Returns the actual name.

    Example: Wade, Dwyane --> Dwyane Wade
    '''
    if string == 'Oubre, Jr., Kelly':
        return 'Kelly Oubre, Jr.' 
    else:
        list_string = string.split(',')
        rv = list_string[1][1:] + ' ' + list_string[0]
        return rv
    

def build_real_roster(link, limiting_domain):
    '''
    Takes a link to a roster page and the limiting domain associated with that page.
    Returns a dictionary containing the player names for that team and their respective urls. This is necessary
    because the stats page contains some multiplicity. We may need these urls later on, so we gather them here.
    '''
    proper_url, soup = make_soup(link, limiting_domain)

    header = soup.find_all("thead")
    table = header[0].next_sibling.next_sibling

    cells = table.find_all('tr')

    rv = {}
    for cell in cells:
        name, link1 = get_name_get_link(cell)
        name = first_last_name(name)
        rv[name] = link1
    return rv


def get_name_get_link(cell):
    '''
    Given a cell in a table containing roster names for a team, returns the 
    name of the player and the link associated with that player (this link may come in handy
    much later when we return the advanced statistics, but this is the time to get it.)
    '''
    td_list = cell.find_all('td')
    link = cell.find_all('a')[0]['href']
    link = 'http://basketball.realgm.com' + link
    name = td_list[1]['rel']
    return name, link


def get_individual_player_data(player_link, limiting_domain):
    '''
    Scrapes an individual player's page for qualitiative data and images 
    for the final presentation.

    Note, if you print the data string, it ends up nicely formatted. However, 
    in its current form, it looks kinda gross.
    '''


    proper_url, soup = make_soup(player_link, limiting_domain, player_switch = True)
    tags = soup.find_all('div', class_ = 'profile-box') #check if reading the request failed

    if tags != []:

        main_tag = tags[0]
        data_string = main_tag.text

        img_tags = main_tag.find_all('img')
        img_links = []
        for tag in img_tags:
            img_links.append(tag['src'])

        honor_tags = soup.find_all('h2')
        award_list = []
        for tag in honor_tags:
            if tag.text == 'NBA Awards & Honors':
                awards = tag.next_sibling.next_sibling.find_all('tr')
                for t in awards:
                    award_list.append(t.text)
        return data_string, img_links, award_list
    else:
        return None, None, None


def aggregate_roster_dict(roster_dict):
    '''
    While it is sometimes helpfulto store this information in roster form, 
    it is also helpful for the final scraping to aggregate the rosters
    into one giant dictionary that maps player names to their links.

    roster_dict is a nested dictionary that maps links to players and players
    to  links   
    '''
    rv = {}

    for team, team_dict in roster_dict.items():
        for player_name, link in team_dict.items():
            rv[player_name] = link

    return rv



def get_top_trade_data(player_name, player_dict, limiting_domain):
    '''
    Recursive function. Given a list of the best trade targets, returns data
    for the top trade target. Also, checks to make sure that none of the 
    options are injured (in other words, the read to their individual page fails)

    player_list is a list of string names of the top trade targets.

    player_dict is a dictionary that maps player links to player names

    returns a tuple containing the player name, data_string, image links, and award_list.
    '''
 
    player_link = player_dict[player_name]
    data_string, img_links, award_list = get_individual_player_data(player_link, limiting_domain)
    if data_string != None: #this means the read failed, or in other words, the player is injured
        return (player_name, data_string, img_links, award_list)


def get_images(trade_option):
    '''
    Trade option is a four-tuple of the form (player, data_string, img_links, award_list).

    the trade option includes links to the images of players. Here, I access the images
    and save them.
    '''
    """
    img_index = 2
    player_index = 0
    team_index = 1

    img_links = trade_option[img_index]
    player_link = img_links[player_index]
    team_link = img_links[team_index]

    player_name = trade_option[player_index]
    player_name = '_'.join(player_name.split())
    team = player_name + '_team'

    path = os.path.abspath('media')

    urllib.request.urlretrieve(player_link, path + '/' + player_name + ".jpg")
    urllib.request.urlretrieve(team_link, path + '/' + team + ".png")
    """
    return None


def make_soup(initial_url, limiting_domain, player_switch = False):
    '''
    Given a url and a limiting domain, returns the proper url 
    and the BeautifulSoup object associated with that page.
    We have this as its own function because we need to both
    generate the links and build the index with the html page.
    Additionally, the html page cannot be reached,
    we return None and an empty list.

    Note: player switch is an indicator that is used to allow us to 
    got to a link we know is good. These links would get blocked
    while crawling, but this is used when getting player stats, 
    in which case we know that the link is good.
    '''
    req1 = get_request(initial_url)
    if req1 == None:
        return None, [] #can't generate request

    proper_url = get_request_url(req1)
    
    if is_url_ok_to_follow(proper_url, limiting_domain):
        text = read_request(req1)
        soup = bs4.BeautifulSoup(text, "html5lib")
        return proper_url, soup
    if player_switch:
        text = read_request(req1)
        soup = bs4.BeautifulSoup(text, "html5lib")
        return proper_url, soup
    else:
        return None, []



def crawl(num_pages_to_crawl,starting_url, limiting_domain):
    '''
    Crawls the course pages and builds the index while it goes.
    Returns final_return_dict, a dictionary of the for {TEAM NAME: [(plater 1, [player 1's stats])...], ...}

    Also returns roster_dict, a dictionary that maps from team name to player to qualitiatve data.
    '''

    steps = 0
    
    proper_url, soup = make_soup(starting_url, limiting_domain)
    starting_links = generate_links(soup, proper_url, limiting_domain)


    roster_dict = turn_starting_links_to_roster_dictionary(starting_links, limiting_domain)    
    return_dict = {}

    visited =  {starting_url} 
    q = list_to_queue(starting_links) 
  
    new_queue, next_link, indicator = get_next_link(visited, q)
    q = new_queue

    
    while(steps <= num_pages_to_crawl and indicator):
        visited.add(next_link) 
        new_proper_url, rv = make_soup(next_link, limiting_domain)
        if rv != []:
            links = generate_links(rv, new_proper_url, limiting_domain) 
            return_dict = get_data(rv, return_dict)
            for link in links:
                if link not in visited:
                    q.put(link) 

        steps += 1 
        new_queue, next_link, indicator = get_next_link(visited, q)

        q = new_queue

   
    final_return_dict =  clean_return_dict(roster_dict, return_dict)
    return final_return_dict, roster_dict


def roster_dict_to_player_info(roster_dict, limiting_domain):
    '''
    Updates the roster dictionary by following the links 
    and scraping all of those pages.

    Returns the updated roster dictionary that maps
    player names to images, awards, descriptions, and stats.
    '''
    updated = {}
    for team, player_dict in roster_dict.items():
        for player, player_link in player_dict.items():
            data_string, img_links, award_list = get_individual_player_data(player_link, limiting_domain)
            updated[player] = {}
            updated[player]['bio'] = data_string
            updated[player]['image'] = img_links
            updated[player]['awards'] = award_list

    return updated

def test_updated_roster_dictionary(updated):
    '''
    Checks through the updated dictionary for players who are injured (the way the website works, if a player is injured,
        our crawler fails scraping the request. Only an injured player would have none for all of these fields.)
    '''
    for player, player_data in updated.items():
        if ((player_data['bio'] == None) and (player_data['image'] == None) and (player_data['awards'] == None)):
            print(player)


def clean_return_dict(roster_dict, return_dict):
    '''
    gets rid of all of the weird categories in the return dictionary from the crawler.
    Additionally, updates names.
    '''
    del return_dict["nba stats leaders"]
   
    rv = eliminate_multiplicity(roster_dict, return_dict)
    return rv

def eliminate_multiplicity(roster_dict, return_dict):
    '''
    Given a dictionary describing the statistics of the entire league (return_dict)
    and roster_dict, a dictionary describing the accurate rosters of the entire league,
    returns a an updated league_statistic dictionary without any multiplicity.

    Also, gets rid of players who were waived or cut.

    '''
    for team, team_stats in return_dict.items():
        new_stats = []

        for player_tupl in team_stats:
            player = player_tupl[0]
            stats = player_tupl[1]

            if player in roster_dict[team]:
                new_stats.append((player, stats))

        return_dict[team] = new_stats

    return return_dict

def build_team_stats_dictionary(league_dictionary):
    '''
    Given a dictionary describing league statistics for every team, 
    uses numpy arrays to find an average statistic vector for each team.
    Returns a dictionary mapping a team name to its average statistics.
    '''

    team_dictionary = {}

    for key, value in league_dictionary.items():
        team_name = key
        tuple_list = value
        
        count = len(tuple_list)
        l = [0] * 20
        sum_ = np.array(l)

        for tup in tuple_list:
            stats = tup[1]
            stats = np.array([float(v) for v in stats])
            print(stats)
            cnt = 0
            '''for s in stats:
                print(type(s))
                cnt += 1
            print('count', cnt)'''
            sum_ += stats

        avg = 1/count * sum_
        avg = list(avg)

        team_dictionary[team_name] = avg

    return team_dictionary



def write_to_JSON(filename):
    '''
    We need to store the data in a JSON for the website.
    Although the combination of dictionary and tuples works nicely for 
    the tasks we need to preform with pandas, I will convert this data into a dictionary.
    '''


    return_dict, roster_dict = crawl(100, starting_url, limiting_domain)
    u = roster_dict_to_player_info(roster_dict, limiting_domain)
    
    with open(filename, 'w') as fp:
        json.dump(u, fp)
