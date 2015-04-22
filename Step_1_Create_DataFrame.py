from __future__ import division

import pandas as pd
from os import listdir, path
import Helpers
import multiprocessing as mp
import sys

def read_chunk(chunk_num, drivers_path, drivers):

    """
    Read one chunk, i.e. a subset of the drivers
    """

    mega_list = []  # List for all drivers of one chunk

    for driver in drivers:

        list_one_driver_all_trips = []  # List for all trips of one driver

        # List trips of a driver
        driver_fullpath = path.join(drivers_path, driver)
        trips = listdir(driver_fullpath)

        # Iterate over trips of one driver and create dataframe
        for trip in trips:

            trip_num = path.splitext(trip)[0]

            df = pd.read_csv(path.join(driver_fullpath, trip))

            # Multi-indices for driver and Trip
            df_with_indices = pd.concat([df], keys = [(driver, trip_num)],
                                              names = ('Driver', 'Trip'))

            # We save all data frames in lists, since this avoids memory errors
            # (the lists are just for temporarily storing the data frames).
            list_one_driver_all_trips.append(df_with_indices)

        # Create dataframe for one driver from trip data frame list
        df_one_driver = pd.concat(list_one_driver_all_trips)

        # Append
        mega_list.append(df_one_driver)

    df_all_drivers = pd.concat(mega_list)

    filename = 'dataframe_{}.h5'.format(chunk_num)

    # Save dataframe in HDF5
    df_all_drivers.to_hdf(path.join(".", filename),
                          'table')

    print("Written to", filename)


def read_all_chunks(drivers_path, drivers, number_of_chunks):
    """
    Reads in all drivers with all their trips and saves them
    to HDF5 files.
    """
    # Split list into parts (depending on memory capacity)
    chunked_drivers = Helpers.chunks(drivers, len(drivers) // number_of_chunks)

    jobs = []

    for chunk_num, drivers in enumerate(chunked_drivers):

        p = mp.Process(target = read_chunk, args = (chunk_num,
                                                    drivers_path,
                                                    drivers, ))
        jobs.append(p)
        p.start()


def main():

    # Number of chunks (depends on memory capacities)
    number_of_chunks = 1

    # All trips and drivers from Kaggle:
    drivers_path = sys.argv[1]

    drivers = listdir(drivers_path)
    read_all_chunks(drivers_path, drivers, number_of_chunks)


if __name__ == "__main__":
    main()