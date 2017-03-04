from time import time
import numpy as np
import matplotlib.pyplot as plt

from sklearn import metrics
from sklearn.cluster import KMeans
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA
from sklearn.preprocessing import scale


import julian_waugh_crawler as JWC


limiting_domain = "basketball.realgm.com"
starting_url = "http://basketball.realgm.com/nba/teams"
limiting_path = "/nba/teams"


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
    for team, team_list in return_dict.items():
        for player_tupl in team_list:
            players += 1
            stats = player_tupl[stats_index]
            name = player_tupl[name_index]

            stats_string_list = [str(x) for x in stats]
            stats_key = ' '.join(stats_string_list)
            s.add(stats_key)

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

        # Step size of the mesh. Decrease to increase the quality of the VQ.
    h = .02     # point in the mesh [x_min, x_max]x[y_min, y_max].

    # Plot the decision boundary. For that, we will assign a color to each
    x_min, x_max = reduced_data[:, 0].min() - 1, reduced_data[:, 0].max() + 1
    y_min, y_max = reduced_data[:, 1].min() - 1, reduced_data[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    # Obtain labels for each point in mesh. Use last trained model.
    Z = kmeans.predict(np.c_[xx.ravel(), yy.ravel()])


    print('we have a result and now need to plot it')
    # Put the result into a color plot
    Z = Z.reshape(xx.shape)

    print(Z)

    
    fig = plt.figure()
    plt.clf()
    plt.imshow(Z, interpolation='nearest',
               extent=(xx.min(), xx.max(), yy.min(), yy.max()),
               cmap=plt.cm.Paired,
               aspect='auto', origin='lower')

    plt.plot(reduced_data[:, 0], reduced_data[:, 1], 'k.', markersize=2)
    # Plot the centroids as a white X
    centroids = kmeans.cluster_centers_
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

def make_centroids(data):
    reduced_data = create_testing_data_positions(data)

    kmeans = KMeans(init='k-means++', n_clusters=5, n_init=10)
    kmeans.fit(reduced_data)
    print(kmeans.cluster_centers_)   


def go():
    data = create_data()
    print('we have data')
    create_general_plot(data, 5)


'''if __name__ == '__main__':
    print('go')
    go()
    pass'''