from time import time
import numpy as np
import matplotlib.pyplot as plt

from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale


import julian_waugh_crawler as JWC

import trader
import pandas as pd
from operator import itemgetter

limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams"


#cluster_map - we had to hardcode because the indices of the centroids change every time and there is some element of qualitative analysis in determinig the positions






def stats_to_name(return_dict):
    '''
    This function tests and idea that I had:
    can we map the stats to the player using a 
    dictionary, with the stats as strings as keys?

    The answer is yes. However, I do not know how long the 
    strings have to be. for example, I know if we have two-component
    stat vectors it will be harder to do the mappings.

    However, seems to work for now.
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






def create_data():
    return_dict = JWC.crawl(100,starting_url, limiting_domain)

    rv = []
    stats_index = 1
    for team, team_list in return_dict.items():
        for player_tupl in team_list:
            stats = player_tupl[stats_index]
            rv.append(stats)
    return rv


def create_general_plot(data, n_positions):
    '''
    Question: scale the data first or not??
    '''
    reduced_data = PCA(n_components=2).fit_transform(data)
    kmeans = KMeans(init='k-means++', n_clusters=n_positions, n_init=10)
    kmeans.fit(reduced_data)
    print(kmeans.cluster_centers_)
    print()

        # Step size of the mesh. Decrease to increase the quality of the VQ.
    h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
    y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    # Obtain labels for each point in mesh. Use last trained model.
    Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])


    #print('we have a result and now need to plot it')
    # Put the result into a color plot
    Z = Z.reshape(xx.shape)

    #print(Z)

    
    fig = plt.figure()
    plt.clf()
    plt.imshow(Z, interpolation='nearest',
               extent=(xx.min(), xx.max(), yy.min(), yy.max()),
               cmap=plt.cm.Paired,
               aspect='auto', origin='lower')

    plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    # Plot the centroids as a white X
    centroids = kmeans.cluster_centers_
    print(type(centroids))
    print(centroids[:, 0])
    print()
    print()
    print(centroids[:, 1])

    plt.scatter(centroids[:, 0], centroids[:, 1],
                marker='x', s=169, linewidths=3,
                color='w', zorder=10)
    plt.title('K-means clustering on the NBA dataset (PCA-reduced data)\n'
              'Centroids are marked with white cross')
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(())
    plt.yticks(())
    #plt.show()


    print('we made the plot and now we need to save it')
    fig.savefig('cluster.pdf')


def create_testing_data_super_star(data):
    '''
    [games_played, minutes_per_game, three pointers made, rebounds per game, assists, steals, blocks, points]

    by including games and minutes, I hope to partition the league into the different classes of positions (starters,
        bench players, injured good players, role players etc)- very cool

    '''
    rv = []

    for vector in data:
        '''print(vector)
        print(type(vector))
        
        a = vector[:2]
        b = vector[5]
        c = vector[-5:] 

        print(a , b , c)'''

        new_vector = vector[:2] + [vector[5]] + vector[-5:]
        rv.append(new_vector)

    return rv

def create_testing_data_positions(data):
    '''
    [three pointers made, rebounds, assists, steals, blocks, points]

    all of these are divided by minutes in order to get actual positions

    by including games and minutes, I hope to partition the league into the different classes of positions (starters,
        bench players, injured good players, role players etc)- very cool

    '''
    rv = []

    for vector in data:
        '''print(vector)
        print(type(vector))
        
        a = vector[:2]
        b = vector[5]
        c = vector[-5:] 

        print(a , b , c)'''
        #minutes = vector[1]
        minutes = 1
        new_vector = np.array([vector[5]] + vector[-5:])
        new_vector = list(new_vector * 1/minutes)

        rv.append(new_vector)

    return rv


def create_testing_data_arthur(data):
    '''
    [games_played, minutes_per_game, three pointers made, rebounds per game, assists, steals, blocks, points]

    by including games and minutes, I hope to partition the league into the different classes of positions (starters,
        bench players, injured good players, role players etc)- very cool

    '''
    rv = []

    three_pt_index = 7
    field_goal_index = 4
    free_throw_index = 10


    for vector in data:
        '''print(vector)
        print(type(vector))
        
        a = vector[:2]
        b = vector[5]
        c = vector[-5:] 

        print(a , b , c)'''

        new_vector = [vector[three_pt_index]] + [vector[free_throw_index]] + [vector[field_goal_index]] + vector[-5:]
        rv.append(new_vector)

    return rv
def make_centroids(data):
    reduced_data = create_testing_data_arthur(data)

    kmeans = KMeans(init='k-means++', n_clusters=5, n_init=10)
    kmeans.fit(reduced_data)


    return kmeans.cluster_centers_ 



def cluster_centers_d_2(data):
    reduced_data = PCA(n_components=2).fit_transform(data)

    print(reduced_data)
    kmeans = KMeans(init='k-means++', n_clusters=5, n_init=10)
    kmeans.fit(reduced_data)
    print(kmeans.cluster_centers_)
    print()


def compare_player_to_centroid(centroid_vector, player_vector, player_name, position):
    '''
    makes a plot comparing the player stats to the stats at the centroid.

    make sure that the vectors are five components long.

    Re-adjust labes later - maybe make them a parameter?


    http://matplotlib.org/examples/pylab_examples/barchart_demo.html


    need to also print this stuff out


    '''
    centroid_vector = [round(x, 2) for x in centroid_vector]
    player_vector = list(player_vector)[0] 

    centroid_percents = centroid_vector[:3]
    player_percents = player_vector[:3]

    centroid_flat = centroid_vector[3:]
    player_flat = player_vector[3:]


    #print(type(centroid_percents), type(player_percents), type(centroid_flat), type(player_flat))
    
   
    #print(centroid_vector)
    #print(player_vector)
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
    #plt.legend(loc= 0)

    plt.tight_layout()
    



    plt.show()


def test_plot():
    c_vector = [11, 15, 40, 0, 3.5]
    player_vector = [25, 9, 20, 3.2, 1]
    compare_player_to_centroid(c_vector, player_vector)









def predict_centroid(reduced_data):
    '''
    predicts the indexes of the cluster.
    Note that you might wanna use fit_predict
    '''
    kmeans = KMeans(init='k-means++', n_clusters=5, n_init=10)
    kmeans.fit(reduced_data)
    #return kmeans
    print(kmeans.cluster_centers_)
    
    print(kmeans.predict(reduced_data))
    #for v in reduced_data:

        #print(kmeans.predict([v]), v)





def make_stat_vector(row_index, league_df):
    percents = ['3P%', 'FG%', 'FT%']
    flats =  ['RPG', 'APG', 'SPG', 'BPG', 'PPG']

    vector = []
    for percent in percents:
        vector += [league_df.iloc[row_index][percent]]
    for flat in flats:
        vector += [league_df.iloc[row_index][flat]]
    return vector




class Cluster_DF(object):

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
        player_position = self.df[self.df['PLAYER'] == player_name]['position']
        #print(player_position)
        centroid_vector = self.centroids[player_position]
        #print(centroid_vector)
        position = self.map[array_to_key(centroid_vector)]

        return position

    def plot(self, player_name):
        player_row = self.df[self.df['PLAYER'] == player_name]

        position = player_row['position']
        centroid_vector = self.centroids[position]
        position_name = self.map[array_to_key(centroid_vector)]

        player_vector =  player_row['vector']
        player_name = player_row['PLAYER']

        compare_player_to_centroid(centroid_vector, player_vector, player_name, position_name)



CLUSTER_CENTERS = {'0.209335480.397296770.591316131.516129030.661935480.277419350.175483872.58516129' : 'Scrub',
                       '0.192682930.506658540.685341467.895121951.70.941463410.8829268311.28536585' : 'Starting Big',
                       '0.363361110.468027780.835888896.316666674.81.197222220.6722222223.48333333' : 'Star',
                        '0.31321250.455618750.73961253.321251.7231250.633750.36757.266875' : 'Role Player',
                        '0.365833330.455516670.81544.486666673.228333330.980.49514.98333333' : 'Starting Guard'}





def make_position_map(centroid_array):
    '''
    This function relies on some level of qualitative analysis. We looked at the 
    positions and realized we could identify out positions based on points per game.
    '''
    role_player_index = 1
    star_index = 4
    scrub_index = 0
    starting_big = 2
    starting_guard = 3

    map_ = {}
    centroid_array = sorted(centroid_array, key = itemgetter(-1))
    #print(centroid_array[0])

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


def go():
    data = create_data()
    print('we have data')
    create_general_plot(data, 5)


'''if __name__ == '__main__':
    print('go')
    go()
    pass'''