import re
import utility as util
import bs4
import queue
import json
import sys
import csv
import scraping
import numpy as np
import json

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






def turn_starting_links_to_roster_dictionary(starting_links, limiting_domain):
    '''
    I am not crawling again. Instead, I will leverage symmetry in website urls.
    Returns a dictionary that maps team name to players and their respective player page links.
    Note that we cannot use this for finding the statistics because
    '''
    add_string = 'Rosters/Regular/2017'
    l = 'http://basketball.realgm.com/nba/stats'
    bad_index = -19


    #this might be the source of multiplicity - maybe delete from other crawler (take care of that later...)
    #use this to leverage multiplicity
    #first thing when you get back - take care of scoring pe


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




s2 = 'http://basketball.realgm.com/nba/teams/Boston-Celtics/2/Stats/2017/Averages'

s3 = 'http://basketball.realgm.com/nba/teams/Memphis-Grizzlies/14/Rosters/Regular/2017'

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

    Example: Wade, Dwayne --> Dwayne Wade
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
    #print(link)
    #print(type(link))
    name = td_list[1]['rel']
    return name, link





player_link = 'http://basketball.realgm.com/player/Tony-Allen/Summary/391'

def get_individual_player_data(player_link, limiting_domain):
    '''
    Scrapes an individual player's page for qualitiative data and images 
    for the final presentation.

    Note, if you print the data string, it ends up nicely formatted. However, 
    in its current form, it looks kinda gross.
    '''


    proper_url, soup = make_soup(player_link, limiting_domain, player_switch = True)

    main_tag = soup.find_all('div', class_ = 'profile-box')[0]
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


    
s4 = 'http://basketball.realgm.com/player/LeBron-James/Summary/250'






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
    req1 = util.get_request(initial_url)
    if req1 == None:
        #print('bad')
        return None, [] #can't generate request

    proper_url = util.get_request_url(req1)
    
    if util.is_url_ok_to_follow(proper_url, limiting_domain):
        text = util.read_request(req1)
        soup = bs4.BeautifulSoup(text, "html5lib")
        return proper_url, soup
    if player_switch:
        #print('swtich')
        text = util.read_request(req1)
        soup = bs4.BeautifulSoup(text, "html5lib")
        return proper_url, soup
    else:
        #print('bad')
        return None, []



def crawl(num_pages_to_crawl,starting_url, limiting_domain):
    '''
    Crawls the course pages and builds the index while it goes.
    Returns the index.
    '''

    steps = 0
    
    proper_url, soup = make_soup(starting_url, limiting_domain)
    starting_links = generate_links(soup, proper_url, limiting_domain)
    #starting_links = [x for x in starting_links if x != bad_link]


    roster_dict = turn_starting_links_to_roster_dictionary(starting_links, limiting_domain)

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



    
    return clean_return_dict(roster_dict, return_dict)



def clean_return_dict(roster_dict, return_dict):
    '''
    gets rid of all of the weird categories in the return dictionary from the crawler.
    Additionally, updates names.
    '''
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




    return eliminate_multiplicity(roster_dict, return_dict)

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




def search_for_multiplicity(return_dict):
    '''
    A test for multiplicity in player names, caused by trades.
    Takes in a dictionary describing the league.
    Returns a dictionary mapping each player who is on 
    multiple teams to the team on which they play.
    '''
    multiplicity = {}
    #s = set()
    
    for team, team_list in return_dict.items():
        for player_tupl in team_list:
            player = player_tupl[0]
            if player not in multiplicity:
                multiplicity[player] = [team]
            else:
                multiplicity[player] += [team]


    #print(multiplicity)
    m =  {}
    for player, teams in multiplicity.items():
        if len(teams) != 1:
            m[player] = teams
    return m


def eliminate_multiplicity(roster_dict, return_dict):
    '''
    Given a dictionary describing the statistics of the entire league (return_dict)
    and roster_dict, a dictionary describing the accurate rosters of the entire league,
    returns a an updated league_statistic dictionary without any multiplicity.
    '''
    multiplicity_dict = search_for_multiplicity(return_dict)

    players_to_elimate = {}
    
    for player, teams in multiplicity_dict.items():
        for team in teams:
            if player not in roster_dict[team]:
                if team not in players_to_elimate:
                    players_to_elimate[team] = {player}
                else:
                    players_to_elimate[team].add(player)
    

    for team in players_to_elimate:
        wrong_players = players_to_elimate[team]
        roster = return_dict[team]

        new_team = []
        for data_tupl in roster:
            player = data_tupl[0]
            if player not in wrong_players:
                new_team.append(data_tupl)
        return_dict[team] = new_team

    return return_dict




def search_for_three_word_names(return_dict):
    '''
    Simple test for three word names. Delete before submitting
    because we don't want them to know about this.

    Alternatively, we could hardcode these guys in.
    '''
    rv = []
    for team, team_list in return_dict.items():
            for player_tupl in team_list:
                player = player_tupl[0]
                name = player.split(' ')
                if len(name) > 2:
                    rv.append(player)
    return rv


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
    with open("pure_stats.csv", 'w') as csvfile5:
        p = 40
        for team in dictionary.keys():
            for x in dictionary[team]:
                stats = x[1]
                player = x[0]
                p += 1
                stat_num = 0
                stat = str(stats)
                for x in stats:
                    stat = str(x)
                    writer = csv.writer(csvfile5, delimiter='|')
                    writer.writerow([player, stat_num, stat]) 
                    stat_num += 1


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


    return_dict = crawl(100, starting_url, limiting_domain)

    player_index = 0
    stats_index = 1

    rv ={}
    for team_name, team_stats in return_dict.items():
        for player_tupl in team_stats:
            player_name = player_tupl[player_index]
            player_stats = player_tupl[stats_index]

            rv[player_name] = {}
            rv[player_name]['TEAM'] = team_name
            rv[player_name]['STATS'] = player_stats

    with open(filename, 'w') as fp:
        json.dump(rv, fp)




