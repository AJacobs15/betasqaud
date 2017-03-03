from sklearn import cluster
import numpy as np


'''
TO DO: 
    1) figure out how to print out cluster in display
    2) figure out how to filter dataframe using clusters
    3) figure out which components to put in the vectors 
    (what stats we think are important)



how to run:
in terminal, run ' sudo pip3 install -U scikit-learn '

use this link for the documentation

'''




def build_vectors():
    vectors = []
    for i in range(10):
        v1 = i
        v2 = i + i^2 + 10
        v3 = i^2 -(i +9) ^ 3
        v = [v1, v2, v3]
        vectors.append(v)
    return vectors



def test():
    vectors = [[0,0,1], [0,1,0], [1,0,0]]
    s = cluster.k_means(vectors,3)
    return s


def find_cluster(centroid_matrix, in_vector):
    '''
    Given a matrix of centroid points a vector, 
    determines which centroid that vector is associated
    with by calculating by minimizing the distance to the centroid points


    Returns storage, the nearest centroid vector to the in_vector.
    '''
    maximum = -1
    storage = None
    for vector in centroid_matrix:
        distance = compute_distance(vector, in_vector)
        if distance > maximum:
            storage = vector
            maximum = distance
    return storage


def compute_distance(vector_1, vector_2):
    '''
    note that vector 1 and vector two are assumed to be numpy arrays.

    they should belong to the same dimensional subsace 
    ( for you proles that means they should have the same number of components)

    returns the length of the distance between the two vectors
    '''

    v1 = np.array(vector_1)
    v2 = np.array(vector_2)

    diff = v1 - v2
    length = np.dot(v1, v2)

    return length ** (1/2)