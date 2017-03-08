import pandas as pd
import julian_waugh_crawler as C
import trader
import selections
import represent


limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams"



'''
Ok here is a summary of everything that is needed to trade.

In this document there is a class called GM. it takes a team name and constraints, which is a 
tuple that looks like this: (categories, minimums, maximums), where categories, minimums and 
maximums are as described in ideal_players in selections.



Additionally, for the GM class to work, there needs to be a LEAGUE_DF global constant and a TEAM_DICT
globabl constant. These are created by first running crawl (a function from julian_waugh_crawler), and then
running one of arthur's functions in trader.py.


Obviously, this then  means that this code will take a while to run because in order to do one trade, all of the
websites need to be scraped. However, we can easily fix that if we have some of the data stored online. (which we do - we have
all of the statistical data stored; that is what I sent julien). I just stored all of the player links in a json file
called links.json. 


Basically, this means that on the input end of this code, somehow (either by running the crawler or by accessing data stored in the 
website), we need to produce twodictionaries in the form of return_dict and roster_dict (if you want to know what these look like, 
run crawl in julian_waugh_crawler and look at the two return values .


After getting these dictionaries, they can be turned into dataframes using Arthur's functions.


The next thing needed to run this code is 'constraints', which I describe above.




Assuming that we can get all of this data in, the code will reate a Cluster dataframe out of
the league dataframe. The cluster dataframe is written in represent.py, but it is basically a class
that clusters all of the data and has methods to make a graph (which will be saved to a pdf file called plot.pdf)
and predict which cluster a player belongs to. This is best used as a globabl constant. It can be made pretty efficiently,
so we should not mind about having to remake it every time.


To run a trade, initialaze a GM object, then call the GM.trade() method.

This will do the following things: (note that at this point, I print everything out because I do know know how it should be returned)
    1) run trader.trade, which will print out values as it goes (ask Arthur about this - I do not know how he wants to store this data)
    2) trader.trade will also return agents, a ranked list of the best players for which to trade
    3) using a method from the cluster DF, we will grab the position fot the best player in the trade.
    4) using another method from the cluster df, we save a pdf plot of the player's stats compared to the cluster centroid.
    5) finally, using the link associated with the top trade target, we scrape their page (again, not the most efficient,
    but I can easily fix this later and store all of the data in a dictionary so we dont have to scrape every trade), returning
    data_string, img_links, and award_list. data_string is a string containing information about the player, img_links
    contains a link of a team logo photo and a player photo, and award list contains information about all of the awards the player
    won in the NBA.

Again, we print everything. However, this information can easily be returned in whatever form you want. Let me know. 

'''

LEAGUE_DF, TEAM_DICT = trader.test_df(switch=False)


#use arthur's code to make your data bases etc; make a league dataframe call it LEAGUE_DF, TEAM_DICT

clusters = represent.Cluster_DF(LEAGUE_DF)


#note - I assume that we will be given the contraints
#for selections.ideal_players in tuple form
#in  the manner (categories, minimums, maximums)


'''
NEED: a LEAGUE_DF, a TEAM_DICT
'''

CATEGORY_INDEX = 0
MINIMUMS_INDEX = 1
MAXIMUMS_INDEX = 2

class GM(object):
    def __init__(self, team, constraints):
        categories = constraints[CATEGORY_INDEX]
        minimums = constraints[MINIMUMS_INDEX]
        maximums = constraints[MAXIMUMS_INDEX]


        #apply the constraints
        constrained_league = selections.ideal_players(LEAGUE_DF, categories, minimums, maximums)

        self.constrained_league = constrained_league

        self.team_df = TEAM_DICT[team]

    def trade(self):

        #run the trade. It will print out values as it goes.
        agents = trader.trade(self.team_df, self.constrained_league)
        print(agents)

        target_player = agents[0]

        #get position

        position = clusters.player_to_position(target_player)
        print(position)

        #make a visual file
        clusters.plot(target_player)

        link = LEAGUE_DF[LEAGUE_DF['PLAYER'] == target_player]['LINK']

        data_string, img_links, award_list = C.get_individual_player_data(link, limiting_domain)

        if ((data_string == None) and (img_links == None) and (award_list == None)):
            print('the player is currently injured')

        print(data_string)
        print(img_links)
        print(award_list)


def get_player(target_list, LEAGUE_DF):
    '''
    recursive function. If players given by target list are injured,
    it returns the next one.

    Write this later. Not necessary for what you need to do next.
    '''
    player = target[0]

    next = False
    pass





