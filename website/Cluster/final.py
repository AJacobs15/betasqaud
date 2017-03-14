import pandas as pd
from .julian_waugh_crawler import *
from .trader import *
from .selections import *
from .represent import *


limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams"



'''
First, we build a league dataframe and a team dictionary using the test_df function, which
is contained in trader.py.

We aggregate the roster dictionary to a league wide dictionary so we can use the league wide dictionary in our trader.

We then cluster everything using a Cluster_DF object form represent.py
'''

RETURN_DICT, ROSTER_DICT = crawl(100, starting_url, limiting_domain)

PLAYER_DICT = aggregate_roster_dict(ROSTER_DICT)

LEAGUE_DF, TEAM_DICT = test_df(ROSTER_DICT, RETURN_DICT, switch=True)




clusters = Cluster_DF(LEAGUE_DF)

CATEGORY_INDEX = 0
MINIMUMS_INDEX = 1
MAXIMUMS_INDEX = 2

class GM(object):
    '''
    A GM object is created for every trade. It contains information about the 
    contraints and the team. The trader method scans the league for possible trades.
    '''
    def __init__(self, team, constraints):
        '''
        Contraint is a tuple of three lists containing the categories, the minimums, and the maximums
        necessary to run the trade.

        Team is a string name for a team (also includes city, so 'Boston Celtics' would be one, not 'Celtics'.
        Note that we don't need to worry about this because people will use a drop down menu, and not type their requests in)
        '''
        categories = constraints[CATEGORY_INDEX]
        minimums = constraints[MINIMUMS_INDEX]
        maximums = constraints[MAXIMUMS_INDEX]
        self.team = team


        #apply the constraints
        constrained_league = ideal_players(LEAGUE_DF, categories, minimums, maximums)

        self.constrained_league = constrained_league

        self.team_df = TEAM_DICT[team]

    def trader(self):
        '''
        Returns a list of the following form: [((trade_option), [chips])...]  Trade option is a four-tuple of the form 
        (player, data_string, img_links, award_list). chips is a list 
        of the best trades from your team for the current player.

        All image files are saved to a folder called media.
        '''

        #run the trade. 
        agents = trade(self.team_df, self.constrained_league, LEAGUE_DF, ROSTER_DICT, self.team)


        rv = []

        for trade_list in agents:
            target_name = trade_list[0]
            trade_option = get_top_trade_data(target_name, PLAYER_DICT, limiting_domain) #get individual information
            get_images(trade_option) #save images

            clusters.plot(target_name) #get graphic

            chips = []
            for trade_chip in trade_list[1:]:
                name = trade_chip['PLAYER']
                chips.append(name)

            rv.append((trade_option, chips))

        return rv

