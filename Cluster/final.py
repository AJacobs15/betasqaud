import pandas as pd
import julian_waugh_crawler as C
import trader
import selections
import represent
import json


limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams"



with open('return_dict.json') as data_file:    
    return_dict = json.load(data_file)

with open('roster_dict.json') as data_file:    
    ROSTER_DICT = json.load(data_file)



LEAGUE_DF, TEAM_DICT = trader.test_df(ROSTER_DICT, return_dict, switch=True)


PLAYER_DICT = C.aggregate_roster_dict(ROSTER_DICT)

clusters = represent.Cluster_DF(LEAGUE_DF)

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
        constrained_league = selections.ideal_players(LEAGUE_DF, categories, minimums, maximums)

        self.constrained_league = constrained_league

        self.team_df = TEAM_DICT[team]

    def trader(self):

        #run the trade. It will print out values as it goes.
        agents = trader.trade(self.team_df, self.constrained_league, LEAGUE_DF, ROSTER_DICT, self.team)


        rv = []

        for trade_list in agents:
            target_name = trade_list[0]
            trade_option = C.get_top_trade_data(target_name, PLAYER_DICT, limiting_domain) #get individual information
            C.get_images(trade_option) #save images

            clusters.plot(target_name) #get graphic

            chips = []
            for trade_chip in trade_list[1:]:
                name = trade_chip['PLAYER']
                chips.append(name)

            rv.append((trade_option, chips))

        return rv




       
        



        '''target_players = []
        if len(agents) >= 5:
            for x in range(5):
                target_players.append(agents[x][1])
        else:
            for x in range(len(agents)):
                target_players.append(agents[x][1])

        #get position
        trade_players = []
        for player in target_players:
            position = clusters.player_to_position(player)
            temp = (player, position)
            trade_players.append(temp)
       

        return trade_players'''


