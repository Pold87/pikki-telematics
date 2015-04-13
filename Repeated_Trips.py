from __future__ import division
import pandas as pd
import numpy as np
from os import path, listdir
from scipy.spatial.distance import cdist
import h5py
import multiprocessing as mp

DISTANCE = 100

# Chunks (containing parts of the mega df)
chunk_path = "/scratch/vstrobel/chunks32"
matched_trips_path = "/scratch/vstrobel/matched/"


def rotational(theta):
    # http://en.wikipedia.org/wiki/Rotation_matrix
    # Beyond rotation matrix, fliping, scaling, shear can be combined into a single affine transform
    # http://en.wikipedia.org/wiki/Affine_transformation#mediaviewer/File:2D_affine_transformation_matrix.svg
    return np.array([[-np.sin(theta), np.cos(theta)], [np.cos(theta), np.sin(theta)]])


def flip(x):
    # flip a trip if more that half of coordinates have y axis value above 0
    if np.sign(x[:,1]).sum() > 0:
        x = x.dot(np.array([[1,0],[0,-1]]))
    return pd.DataFrame(x, columns=['x', 'y'])


def rotate_trip(trip):
    # take last element
    a = trip.iloc[-1]
    # get the degree to rotate
    w0 = np.arctan2(a.y,a.x) # from origin to last element angle
    # rotate using the rotational: equivalent to rotational(-w0).dot(trip.T).T
    return np.array(trip.dot(rotational(w0)))

    
def compressed_trip(trip):

    """
    Create a new representation of the trips by using only the
    points in time that surpass a distance threshold, while the
    intermediate points are discarded.

    """

    diff1 = np.diff(trip.x) ** 2
    diff2 = np.diff(trip.y) ** 2
    euc_dist = np.sqrt(diff1 + diff2)

    euc_cum = np.cumsum(euc_dist)
    
    sol = []
    for i in range(int((euc_cum[-1]) / DISTANCE)):
        sol.append(next(j for j in range(len(euc_cum))
                        if euc_cum[j]-(i * DISTANCE) >= 0))

    sol_arr = np.array(sol, dtype = int)
    return trip.ix[sol_arr]

def similarity_trips(trips):

    """
    Calculate similarity between two trips, the pseuocode can be
    found in the file trip_matchingpseudo.odt

    """

    # Create matrix for similarities
    sim = np.zeros((201, 201))

    # Iterate over all trips from one driver
    for trip_num, trip in trips.groupby(level = ['Trip']):
        max_sim = sim[trip_num, :].max()
        for other_trip_num, other_trip in trips.groupby(level=['Trip']):
            if (trip_num != other_trip_num) or (sim[trip_num, other_trip_num] == 0):

                if len(trip) > len(other_trip):
                    lt = trip  # longer trip
                    st = other_trip  # shorter trip
                else:
                    lt = other_trip
                    st = trip

                dist = len(lt) - len(st)
                dnf = (len(st)/len(lt))  # distance normalization factor

                if dnf > max_sim:
    
                    max_sim_rough = 0
                    top_i = 0                    

                    for i in range(0, dist, 20):
                        new_lt = pd.DataFrame() 
                        new_lt['x'] = lt.x - lt.ix[i, 'x'] 
                        new_lt['y'] = lt.y - lt.ix[i, 'y'] 
                        b = new_lt.iloc[i+len(st)] 
                        beta = np.arctan2(b.y,b.x) 
                        # from origin to last element angle 
                        rlt = np.array(new_lt.dot(rotational(beta)))
                        rst = np.array(st.dot(rotational(beta)))
                        
                        tmp_dis = np.diagonal(cdist(rlt[i:i+len(rst)], rst))
                        sim_pts = (((DISTANCE/2)-tmp_dis) > 0).mean()
                        
                        if sim_pts > max_sim_rough:
                            max_sim_rough = sim_pts
                            top_i = i
                            
                    if (max_sim_rough * dnf) > (max_sim * 0.9):
                        
                        if top_i - 10 < 0:
                            ran_sta = 0
                        else:
                            ran_sta = top_i - 10
                            
                        if top_i + 10 > dist:
                            ran_end = dist
                        else:
                            ran_end = top_i + 10
                            
                        for j in range(ran_sta, ran_end, 1):
                            new_lt = pd.DataFrame() 
                            new_lt['x'] = lt.x - lt.ix[j, 'x'] 
                            new_lt['y'] = lt.y - lt.ix[j, 'y'] 
                            b = new_lt.iloc[i+len(st)] 
                            beta = np.arctan2(b.y,b.x) 
                            # from origin to last element angle 
                            rlt = np.array(new_lt.dot(rotational(beta)))
                            rst = np.array(st.dot(rotational(beta)))
                            
                            tmp_sim = np.diagonal(cdist(rlt[j:j+len(rst)], rst))
                            sim_pts = (((DISTANCE/2)-tmp_sim) > 0).mean()
                            
                            if (sim_pts * dnf) > max_sim: 
                                
                                max_sim = sim_pts * dnf 
                                
                                sim[trip_num, other_trip_num] = max_sim 
                                sim[other_trip_num, trip_num] = max_sim 
    return sim

def preprocessing(driver, trips):
    
    ls_trips = []
    
    for trip_num, trip in trips.groupby(level=['Trip']):
        ls_trips.append(pd.concat([compressed_trip(flip(rotate_trip(trip)))],
                                    keys = [(driver, trip_num)],
                                    names = ('Driver', 'Trip')))

    return pd.concat(ls_trips)

def do_jobs(chunk):

    df = pd.read_hdf(path.join(chunk_path, chunk), key = 'table')

    for driver, trips in df.groupby(level = ['Driver']):
        new_trips = preprocessing(driver, trips)
        sims = similarity_trips(new_trips)
        h5f = h5py.File(matched_trips_path + 'data-{}.h5'.format(driver), 'w')
        h5f.create_dataset('dataset_{}'.format(driver), data=sims)
        h5f.close()

def main():
    
    chunks = listdir(chunk_path)

    jobs = []
    
    for chunk in chunks:
        p = mp.Process(target = do_jobs, args = (chunk, ))
        jobs.append(p)
        p.start()

if __name__ == "__main__":
    main()
