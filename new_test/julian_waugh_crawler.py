import re
import utility as util
import bs4
import queue
import json
import sys
import csv
import scraping
import numpy as np

limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams"



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
        new_url = util.remove_fragment(url)

        converted_url = util.convert_if_relative_url(proper_url, new_url)


        converted_url = str(converted_url)
        if converted_url != None:
            if util.is_url_ok_to_follow(converted_url, limiting_domain):
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



def make_soup(initial_url, limiting_domain):
    '''
    Given a url and a limiting domain, returns the proper url 
    and the BeautifulSoup object associated with that page.
    We have this as its own function because we need to both
    generate the links and build the index with the html page.
    Additionally, the html page cannot be reached,
    we return None and an empty list.
    '''
    req1 = util.get_request(initial_url)
    if req1 == None:
        return None, [] #can't generate request

    proper_url = util.get_request_url(req1)
    
    if util.is_url_ok_to_follow(proper_url, limiting_domain):
        text = util.read_request(req1)
        soup = bs4.BeautifulSoup(text, "html5lib")
        return proper_url, soup
    else:
        return None, []



def crawl(num_pages_to_crawl,starting_url, limiting_domain):
    '''
    Crawls the course pages and builds the index while it goes.
    Returns the index.
    '''

    steps = 0
    
    proper_url, soup = make_soup(starting_url, limiting_domain)
    starting_links = generate_links(soup, proper_url, limiting_domain)


    #print(starting_links)
    
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
            


            return_dict = scraping.get_data(rv, return_dict)
            
            
            for link in links:
                if link not in visited:
                    q.put(link) 

        steps += 1 
        new_queue, next_link, indicator = get_next_link(visited, q)

        q = new_queue



    
    return clean_return_dict(return_dict)



def clean_return_dict(return_dict):
    del return_dict["Scoring Per"]
    return_dict['Los Angeles Lakers'] = return_dict.pop('Los Angeles')
    return_dict['Golden State Warriors'] = return_dict.pop('Golden State')
    return_dict['New York Knicks'] = return_dict.pop('New York')
    return_dict['Oklahoma City Thunder'] = return_dict.pop('Oklahoma City')
    return_dict['San Antonio Spurs'] = return_dict.pop('San Antonio')
    return_dict['Portland Trail Blazers'] = return_dict.pop('Portland Trail')
    return_dict['New Orleans Pelicans'] = return_dict.pop('New Orleans')

    '''for team, stat_list in return_dict.items():

        s = set()
        nl = []
        for player_tupl in stat_list:
            
            name = player_tupl[0]
            stats = player_tupl[1]
            if name not in s:
                s.add(name)
                nl.append((name, stats))
        return_dict[team] = nl'''




    return return_dict

def test1(d):
    team = d["Boston Celtics"]
    print(len(team))
    s = set()
    cnt = 0
    for player_t in team:
        name = player_t[0]
        stats = player_t[1]
        if name not in s:
            
            print(name)
            print(stats)
            print()
            cnt += 1
            s.add(name)
    return cnt




def create_csv(dictionary):
    with open('team_id.csv', 'w') as csvfile1: # creating id_table for team
        t = 1
        p = 40
        for team in dictionary.keys():
            t_id = t
            t += 1
            writer = csv.writer(csvfile1, delimiter='|')
            writer.writerow([t_id, team])
    with open('player_id.csv', 'w') as csvfile2: # creating id_table for player
        t = 1
        p = 40
        for team in dictionary.keys():
            t_id = t
            t += 1
            for x in dictionary[team]:
                player = x[0]
                stats = x[1]
                p_id = p 
                p += 1
                writer = csv.writer(csvfile2, delimiter='|')
                writer.writerow([p_id, player])       
    with open('team_players.csv', 'w') as csvfile3: # creating players on team
        t = 1
        p = 40
        for team in dictionary.keys():
            t_id = t
            t += 1
            for x in dictionary[team]:
                player = x[0]
                stats = x[1]
                p_id = p 
                p += 1
                writer = csv.writer(csvfile3, delimiter='|')
                writer.writerow([p_id, player, t_id, team])
    with open('player_stats.csv', 'w') as csvfile4: # creating stats for each player
        t = 1
        p = 40
        for team in dictionary.keys():
            t_id = t
            t += 1
            for x in dictionary[team]:
                player = x[0]
                stats = x[1]
                p_id = p 
                p += 1
                stat = str(stats)
                writer = csv.writer(csvfile4, delimiter='|')
                writer.writerow([p_id, player, t_id, team, stat])   



def test(d):
    s = set()

    dic = {}
    cnt = 0
    for k, v in d.items():
        for val in v:
            name = val[0]
            stats = val[1]
            if name not in s:
                s.add(name)
            else:
                cnt += 1
                if name not in dic:
                    dic[name] = [k]
                else:
                    dic[name].append(k)
                print(name, stats)
                print()
    return cnt, dic
          


def test2(d):
    for k, v in d.items():
        if len(v) > 15:
            print(k, len(v))
def test3(d):
    for k, v in d.items():
        print(k, len(v))

def test4(d):
    s = set()
    for k in d.keys():
        if k not in s:
            s.add(k)
        else:
            print("duplicate", k)

'''
            s.append()
    s2 = set(s)

    print(len(s))
    print(len(s2))
    if len(s) != len(s2):
        return False
    else:
        return True

'''



def build_team_stats_dictionary(league_dictionary):

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
    