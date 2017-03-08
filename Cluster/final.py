import pandas as pd
import julian_waugh_crawler as C
import trader
import selections


limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams"


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
        maximums = contraints[MAXIMUMS_INDEX]

        self.contrained_league = selections.ideal_players(LEAGUE_DF, categories, minimums, maximums)

        self.team_df = TEAM_DICT[team]

    def trade(self):


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





