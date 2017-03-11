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

We then cluster everything using a CLUDTER_DF object form represent.py
'''

LEAGUE_DF, TEAM_DICT = test_df(switch=False)




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


        #apply the constraints
        constrained_league = ideal_players(LEAGUE_DF, categories, minimums, maximums)

        self.constrained_league = constrained_league

        self.team_df = TEAM_DICT[team]

    def trader(self):

        #run the trade. It will print out values as it goes.
        agents = trade(self.team_df, self.constrained_league, LEAGUE_DF)

        target_players = []
        if len(agents) >= 5:
            for x in range(5):
                target_players.append(agents[x][1]["PLAYER"])
        else:
            for x in range(len(agents)):
                target_players.append(agents[x][1]["PLAYER"])

        #get position
        trade_players = []
        for player in target_players:
            position = clusters.player_to_position(player)
            temp = player + ": " + position
            trade_players.append(temp)
       

        return trade_players


def get_player(target_list, LEAGUE_DF):
    '''
    recursive function. If players given by target list are injured,
    it returns the next one.

    Write this later. Not necessary for what you need to do next.
    '''
    player = target[0]

    next = False
    pass





