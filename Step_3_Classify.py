from __future__ import division

import pandas as pd
import numpy as np
from os import path, listdir
from sklearn.base import ClassifierMixin, BaseEstimator
from sklearn.ensemble import RandomForestClassifier
import multiprocessing as mp
import sys


class EnsembleClassifier(BaseEstimator, ClassifierMixin):
    """
    Use several classifiers and compute their mean as prediction
    """

    def __init__(self, classifiers=None):
        self.classifiers = classifiers
        self.predictions_ = list()

    def fit(self, x, y):
        for classifier in self.classifiers:
            classifier.fit(x, y)

    def predict_proba(self, x):
        for classifier in self.classifiers:
            self.predictions_.append(classifier.predict_proba(x))
            m = np.mean(self.predictions_, axis=0)
        return m


def create_submission_file(df):
    """
    Create a submission file for kaggle from a data frame
    """

    # Find file number for new file
    file_num = 0
    while path.isfile('submission-{}.csv'.format(file_num)):
        file_num += 1

    # Write final submission
    df.to_csv('submission-{}.csv'.format(file_num), index=False)


def classify(f, df_list, features_path):
    """
    Preprocess data frames, trips in this chunk and perform classification 
    """

    # Preprocessing to set data type of columns
    feature_df = pd.read_hdf(path.join(features_path, f), key='table')
    feature_df.reset_index(inplace=True)
    feature_df['Driver'] = feature_df.Driver.astype('int')
    feature_df['Trip'] = feature_df.Trip.astype('int')
    sorted_df = feature_df.sort(['Driver', 'Trip'])

    calculated = []

    for i, (d, driver_df) in enumerate(sorted_df.groupby('Driver')):

        # Amount of other drivers (negative set)
        amount_others = 200

        # Indices to get other drivers from
        indeces = np.append(np.arange(i * 200),
                            np.arange((i+1) * 200, len(feature_df)))

        other_trips = indeces[np.random.randint(0,
                                                len(indeces) - 1,
                                                amount_others)]
        others = feature_df.iloc[other_trips]

        # Set label of other drivers to 0
        others.Driver = np.repeat(int(0), amount_others)

        # Perform classification
        submission_df = calc_prob(driver_df, others)

        # Append to the final submission dataframe
        calculated.append(submission_df)

    df_list.append(pd.concat(calculated))

    
def calc_prob(df_features_driver, df_features_other):

    """
    Trains the classifier and creates a data frame for the
    submission containing the driver/trip id and the probability
    """

    df_train = df_features_driver.append(df_features_other)
    df_train.reset_index(inplace=True)
    df_train.Driver = df_train.Driver.astype(int)

    model = RandomForestClassifier(n_estimators=1000,
                                   min_samples_leaf=2,
                                   max_depth=5)

    feature_columns = df_train.iloc[:, 4:]

    # Train the classifier
    model.fit(feature_columns, df_train.Driver)

    df_submission = pd.DataFrame()

    df_submission['driver_trip'] = create_first_column(df_features_driver)

    # Return array with the probability for every driver
    probs_array = model.predict_proba(feature_columns[:200])
    probs_df = pd.DataFrame(probs_array)

    df_submission['prob'] = np.array(probs_df)

    return df_submission

    
def create_first_column(df):
    """
    Create first column for the submission csv, e.g.
    driver_trip
    1_1
    1_2
    """
    return df.Driver.apply(str) + "_" + df.Trip.apply(str)


def main():

    # Get data frame that contains each trip with its features
    # features_path = "/scratch/vstrobel/features_opti_32/"
    features_path = sys.argv[1]
    features_files = sorted(listdir(features_path))

    # Create a manager for managing variables when using multiprocessing
    manager = mp.Manager()
    df_list = manager.list()

    jobs = []

    for f in features_files:
        p = mp.Process(target = classify, args = (f,
                                                  df_list,
                                                  features_files, ))
        jobs.append(p)
        p.start()

    [job.join() for job in jobs]

    final_list = []

    for l in df_list:
        final_list.append(l)

    submission_df = pd.concat(final_list)
    create_submission_file(submission_df)

if __name__ == "__main__":
    main()
