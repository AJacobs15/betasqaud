import re
import utility
import bs4
import queue
import json
import sys
import csv

INDEX_IGNORE = set(['a',  'also',  'an',  'and',  'are', 'as',  'at',  'be',
                    'but',  'by',  'course',  'for',  'from',  'how', 'i',
                    'ii',  'iii',  'in',  'include',  'is',  'not',  'of',
                    'on',  'or',  's',  'sequence',  'so',  'social',  'students',
                    'such',  'that',  'the',  'their',  'this',  'through',  'to',
                    'topics',  'units', 'we', 'were', 'which', 'will', 'with', 'yet'])

limiting_path = "/nba"
limiting_domain = "sports.yahoo.com"
starting_url = "http://sports.yahoo.com/nba/teams/"
player_url = "https://sports.yahoo.com/nba/players/5066/"
roster_url = "http://sports.yahoo.com/nba/teams/gsw/roster"
bad_url = "http://sports.yahoo.com/thevertical/woj/"

def generate_links(initial_url):
    '''
    Takes a url as input. Returns the urls of all of the pages linked 
    to the initial page in list format. Note that for the final version 
    that does not only crawl the web, we will also want to get information
    off of these web pages.

    NOTE: we have yet to use the function get_request_url. There is 
    thus something missing from our implementation.

    NOTE: we may have to take into account more situations where the 
    return value of getting a request is None.

    NOTE: should we have an a different return value than the empty list if 
    we can't find any links?

    NOTE: function fails with this link:
    http://www.classes.cs.uchicago.edu/archive/2015/winter/12200-1/new.collegecatalog.uchicago.edu/thecollege/thecurriculum.1.html

    I DON'T KNOW WHY!
    '''
    #reach out to web page
    req1 = util.get_request(initial_url)
    if req1 == None:
        return [] #can't generate request

    proper_url = util.get_request_url(req1)
    
    if util.is_url_ok_to_follow(proper_url, limiting_domain):
        text = util.read_request(req1)
        soup = bs4.BeautifulSoup(text, "html5lib")
        links_list = soup.find_all("a")


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

def test_2():
    s = {1,2,3,4, 5, 6, 7, 8, 9, 10, 11}
    q =  queue.Queue()
    q.put("dog")
    #for term in range(5, 20):
        #q.put(term)
    return get_next_link(s, q)


            


def test_1():
    '''
    .put - puts item into queue
    .get - pops item from queue
    .empty - tells you when queue is empty

    The lists should be the same. In other words,
    the first to enter the queue should be the first 
    out.
    '''

    q =  queue.Queue()
    for term in range(10):
        q.put(term)

    i = 0
    while i < 10:
        print(i, q.get())
        i += 1
    if q.empty():
        print("The queue is Empty!")



phys_link = "https://www.classes.cs.uchicago.edu/archive/2015/winter/12200-1/new.collegecatalog.uchicago.edu/thecollege/physics/index.html"

def get_index(url):
    req1 = util.get_request(url)
    text = util.read_request(req1)
    soup = bs4.BeautifulSoup(text, "html5lib")
    course_tags = soup.find_all('div', class_="courseblock main")
    classes = []
    for clas in course_tags:
        classtitle_tags = clas.find_all('p', class_='courseblocktitle')
        classdesc_tags = clas.find_all('p', class_='courseblockdesc')

        nl = []

        for t_tag in classtitle_tags:
            nl.append(t_tag.text)

        for d_tag in classdesc_tags:
            nl.append(d_tag.next)



        classes.append(tuple(nl))
    return classes

def get_dict_from_json(filename):
    '''
    Takes a json file and returns it as a dictionary.
    '''
    json1_file = open(filename)
    json1_str = json1_file.read()
    json1_data = json.loads(json1_str)
    return json1_data

def test_getting_dict():
    '''
    This is just a testing function that will take a 
    the course info taken from test_course_page
    and convert it into a dictionary with the 
    course code and a list of all the words in the description
    '''
    course_map = get_dict_from_json('course_map.json')
    courses = test_course_page()
    test_dict = {}
    for course in courses:
        new_str = course[1].lower()
        temp_str = re.sub('[\d().,-;:]','',new_str)
        new_desc = temp_str.split()
        for word in INDEX_IGNORE:
            for desc in list(new_desc):
                if desc == word:
                    new_desc.remove(word)
        course_key = ''
        course_name = course[0].replace('\xa0',' ')
        print(course_name)
        for key in course_map:
            a = re.search(key+'.',course_name)
            if a:
                course_key = course_map[key]
        for desc in new_desc:
            if desc not in test_dict:
                test_dict[desc] = [course_key]
            else:
                temp = []
                temp += test_dict[desc]
                temp.append(course_key)
                test_dict[desc] = temp
    return test_dict

def test_course_page(visited_set):
    '''
   
    '''

    html = open('physics.html').read()
    soup = bs4.BeautifulSoup(html, "lxml")
    DIV_tag_list = soup.find_all('div', class_="courseblock main") #if there are no tags with courseblock main, this will return an empty list
    
    if DIV_tag_list != []: #if this page does indeed have a class callled courseblock main

        rv = []
        for tag in DIV_tag_list:
            main_tuple = get_title_get_description(tag)
            rv.append(main_tuple)
            
            sub_tags_list = util.find_sequence(tag)
            if sub_tags_list != []:  #in this case, the object is a sequence. Thus, the subsequences will map key words to the title, allowing us to avoid parsing a difficult title
                for sub_tag in sub_tags_list:
                    out = get_title_get_description(sub_tag)
                    rv.append(out)
            else: #in this case, there are no subsequences, so we are dealing with a single quarter course. we must thus try and add the title
                print("dog")
                #in here we would extract information from the tag TITLE itself; either

                #NOTE: either way, we will be mapping the text in the title to every subsequence (if they exist) 
        return rv

            
            
        


        '''

        for tag in DIV_tag_list:
            if not util.is_whitespace(tag): #I am including this because this helper function exists so I am assuming you can sometimes get fucked up tags, however, this is kind of a crapshoot






            paragraph_title_list = tag.find_all('p', class_="courseblocktitle")
            for p in paragraph_tag_list:
                print(p.text)
        '''


    


    '''
    for tag in tag_list:
        print(tag.text) #this gets all of the titles and descriptions

    list_two = soup.find_all('div', class_="courseblock detail")
    for term in list_two:
        print(term.text)

     for tag in tag_list:
        sub_seq = util.find_sequence(tag)
        if sub_seq != []:
            print(sub_seq.text)

    html = open('class_page_info.html').read()
    soup = bs4.BeautifulSoup(html)
    print(html)
    '''

def get_title_get_description(in_tag):
    '''
    takes a tag and returns a dictionary containing important information about the
    '''
    
    #get all of the tags for the title and description
    classtitle_tags = in_tag.find_all('p', class_='courseblocktitle')
    classdesc_tags = in_tag.find_all('p', class_='courseblockdesc')

    rv = []

    #get title
    for t_tag in classtitle_tags:
        rv.append(t_tag.text)

    #get description
    for d_tag in classdesc_tags:
        rv.append(d_tag.text)



    
    return tuple(rv)





practice_title = 'PHYS 12100-12200-12300.  General Physics I-II-III.'
def get_title_and_title_words(string):
    match=re.findall('[A-Z]+ [0-9-]+.  [A-Z][\w\d]*', string)
    for term in match:
        print(term)



'([A-Z]+) (([0-9]{5})-){2}([0-9]{5})  ([A-Z][\w\d]*)'
