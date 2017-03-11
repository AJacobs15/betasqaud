from time import time
import numpy as np
import matplotlib.pyplot as plt

from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale


from .julian_waugh_crawler import *

from .trader import *
import pandas as pd
from operator import itemgetter

limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams"



'''
GENERAL INFORMATION

The mot important part of this document is the Cluster_DF object, which creates clustering based on 
the league dataframe, which we build in trader.py

Note that we do not normalize the vectors because then the cluster centroids are meaningless.
Each of their components contains a statistics, so if normalized, they would no longer accurately
reflect league preformance. While this may lead to some innacuracies (weighting of flat statistics 
much higher than percentages), it still allows us to partition the league into some very interesting
clusters.



'''


def stats_to_name(return_dict):
    '''
    This function tests an idea that I had:
    can we map the stats to the player using a 
    dictionary, with the stats as strings as keys?

    The answer is yes. However, I do not know how long the 
    strings have to be. for example, I know if we have two-component
    stat vectors it will be harder to do the mappings.

    However, seems to work for now.

    Note: it does not work for the size of the tuples that we use. (they are smaller
        then the full size)

    '''

    s= set()

    players = 0

    stats_index = 1
    name_index = 0
    three_pt_index = 7
    field_goal_index = 4
    free_throw_index = 10

    for team, team_list in return_dict.items():
        for player_tupl in team_list:
            players += 1
            stats = player_tupl[stats_index]
            name = player_tupl[name_index]

            stats = [stats[three_pt_index]] + [stats[free_throw_index]] + [stats[field_goal_index]] + stats[-5:]

            stats_string_list = [str(x) for x in stats]
            stats_key = ' '.join(stats_string_list)
            if stats_key not in s:
                s.add(stats_key)
            else:
                print(name, stats)

    print('nba size', players)
    print('dictionary size', len(s))

def create_testing_data(data):
    '''
    data should be a nested list of player statistics.

    Returns a new nested list that has all of the statistics that we are looking at. 

    [three pointer percentage, free throw percentage, field goal percentage, rebounds per game, assists, steals, blocks, points]

    by including games and minutes, I hope to partition the league into the different classes of positions (starters,
        bench players, injured good players, role players etc)- very cool

    '''
    rv = []

    three_pt_index = 7
    field_goal_index = 4
    free_throw_index = 10


    for vector in data:
        new_vector = [vector[three_pt_index]] + [vector[free_throw_index]] + [vector[field_goal_index]] + vector[-5:]
        rv.append(new_vector)

    return rv



def make_centroids(data):
    '''
    Some simple code to easily look at the centroids of one of our clusters. 
    '''
    reduced_data = create_testing_data_arthur(data)

    kmeans = KMeans(init='k-means++', n_clusters=5, n_init=10)
    kmeans.fit(reduced_data)


    return kmeans.cluster_centers_ 



def compare_player_to_centroid(centroid_vector, player_vector, player_name, position):
    '''
    makes a plot comparing the player stats to the stats at the centroid.

    Saved to plot.jpeg.

    Compares the flat stats and the percentages separately.

    Inspired by this code: http://matplotlib.org/examples/pylab_examples/barchart_demo.html

    '''
    centroid_vector = [round(x, 2) for x in centroid_vector]
    player_vector = list(player_vector)[0] 

    centroid_percents = centroid_vector[:3]
    player_percents = player_vector[:3]

    centroid_flat = centroid_vector[3:]
    player_flat = player_vector[3:]

    n_groups = len(centroid_vector)


    fig, ax = plt.subplots()

    plt.clf()
    ax1 =fig.add_subplot(211)

    index = np.arange(len(centroid_flat))
    bar_width = 0.35
    opacity = 0.7
    error_config = {'ecolor': '0.3'}
    rects1 = plt.bar(index, centroid_flat, bar_width,
                     alpha=opacity,
                     color='k',
                     error_kw=error_config,
                     label='Generic ' + position)

    rects2 = plt.bar(index + bar_width, player_flat, bar_width,
                     alpha=opacity,
                     color='r',
                     error_kw=error_config,
                     label= player_name)

    plt.xlabel('Categories')
    plt.ylabel('stats')
    plt.title('Comparison of Player to Average Hard stats\n'
                'Position = ' + position)
    plt.xticks(index + bar_width / 2, ('RPG', 'APG', 'SPG', 'BPG', 'PPG'))
    plt.legend(loc= 0)
    plt.tight_layout()

    ax2 =fig.add_subplot(212)

    index = np.arange(len(player_percents))
    bar_width = 0.35

    opacity = 0.7
    error_config = {'ecolor': '0.3'}

    rects1 = plt.bar(index, centroid_percents, bar_width,
                     alpha=opacity,
                     color='k',
                     error_kw=error_config,
                     label='Centroid')

    rects2 = plt.bar(index + bar_width, player_percents, bar_width,
                     alpha=opacity,
                     color='r',
                     error_kw=error_config,
                     label= player_name)

    plt.xlabel('Categories')
    plt.ylabel('stats')



    plt.title('Comparison of Player to Average Percentage stats\n'
                'Position = ' + position)
    plt.xticks(index + bar_width / 2, ('3P%', 'FG%', 'FT%'))
    plt.tight_layout()
    


    fig.savefig('plot.pdf') 


def make_stat_vector(row_index, league_df):
    '''
    Given a row in the league data frame, gets the important statistics associated
    with that player. 

    Returns a list of these statistics, which I abstract as a vector in 8 dimensional euclidean space.
    '''
    percents = ['3P%', 'FG%', 'FT%']
    flats =  ['RPG', 'APG', 'SPG', 'BPG', 'PPG']

    vector = []
    for percent in percents:
        vector += [league_df.iloc[row_index][percent]]
    for flat in flats:
        vector += [league_df.iloc[row_index][flat]]
    return vector




class Cluster_DF(object):
    '''
    Cluster_DF is a class that uses a dataframe to generate clustering of players in the league (hence the creative name)

    Given a player name, it can tell you the position of that player. Alternatively, it can plot where that player stands 
    in relation to the cluster centroids.
    '''

    def __init__(self, league_df):
        
        stat_matrix = []
        for i in range(len(league_df)):
            stat = make_stat_vector(i, league_df)
            stat_matrix.append(stat)
                
        kmeans = KMeans(init='k-means++', n_clusters=5, n_init=10)
        kmeans.fit(stat_matrix)

        centroid_array = kmeans.cluster_centers_

        positions = kmeans.predict(stat_matrix)

        league_df['vector'] = pd.Series(stat_matrix, index = league_df.index)
        league_df['position'] = pd.Series(positions, index = league_df.index)

        

        self.df = league_df
        self.centroids = kmeans.cluster_centers_

        self.map = make_position_map(centroid_array)
    

    def player_to_position(self, player_name):
        '''
        Given a player name, tells you the position of that player.
        '''
        player_position = self.df[self.df['PLAYER'] == player_name]['position']
        centroid_vector = self.centroids[player_position]
        position = self.map[array_to_key(centroid_vector)]

        return position

    def plot(self, player_name):
        '''
        Plots the stats of a player in relation to the cluster centroid. Plot is saved in a 
        file named 'plot.pdf'
        '''
        player_row = self.df[self.df['PLAYER'] == player_name]

        position = player_row['position']
        centroid_vector = self.centroids[position]
        position_name = self.map[array_to_key(centroid_vector)]

        player_vector =  player_row['vector']
        player_name = player_row['PLAYER']

        compare_player_to_centroid(centroid_vector, player_vector, player_name, position_name)



def make_position_map(centroid_array):
    '''
    This function relies on some level of qualitative analysis. We looked at the 
    positions and realized we could identify out positions based on points per game.

    Returns a dictionary which maps the cluster centers to the names of our positions.
    '''
    role_player_index = 1
    star_index = 4
    scrub_index = 0
    starting_big = 2
    starting_guard = 3

    map_ = {}
    centroid_array = sorted(centroid_array, key = itemgetter(-1))

    map_[array_to_key(centroid_array[role_player_index])] = 'Role Player'
    map_[array_to_key(centroid_array[star_index])] = 'Star'
    map_[array_to_key(centroid_array[scrub_index])] = 'Scrub'
    map_[array_to_key(centroid_array[starting_big])] = 'Starting Big'
    map_[array_to_key(centroid_array[starting_guard])] = 'Starting Guard'

    return map_



def array_to_key(array):
    '''
    turns an array into a string for hashing.
    '''
    l = [str(x) for x in array]
    s = ''.join(l)
    return s
