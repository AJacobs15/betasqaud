import re
import utility as util
import bs4
import queue
import json
import sys
import csv

limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams"


def generate_links(initial_url):
    '''
    Takes a url as input. Returns the urls of all of the pages linked 
    to the initial page in list format. Note that for the final version 
    that does not only crawl the web, we will also want to get information
    off of these web pages.
    '''
    #reach out to web page

    req1 = util.get_request(initial_url)

    if req1 == None:
        print("Uh oh")
        return [] #can't generate request

    proper_url = util.get_request_url(req1)
    print(proper_url)
    
    if util.is_url_ok_to_follow(proper_url, limiting_domain):
        print("following")
        text = util.read_request(req1)
        soup = bs4.BeautifulSoup(text, "html5lib")
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

    else:
        print("else")
        return []

def crawl(num_pages_to_crawl):
    '''
    Crawls the course page. Right now, returns a list of viable links.
    However, we will update it to return the index.
    '''

    steps = 0
    
    starting_links = generate_links(starting_url) #get links for starting web page
    

    visited_links = [starting_url]
    visited =  {starting_url} #set with initioal sight
    q = list_to_queue(starting_links) #make the first queue

  
    new_queue, next_link, indicator = get_next_link(visited, q)
    q = new_queue

    while(steps <= num_pages_to_crawl and indicator):
        visited.add(next_link) #put the link we are on in the set
        links = generate_links(next_link) #get the links associated with the current page
        if links != []:
            for link in links:
                if link not in visited:
                    q.put(link) #put the links in the queue
        visited_links += [next_link] # put the page where we are looking in the return value
        
        steps += 1 #increment steps
        new_queue, next_link, indicator = get_next_link(visited, q) #start the next round
        q = new_queue
        #print("RETURN VALUE", rv)
        print(next_link)
        #print(starting_links)
    return visited_links
    

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