import pandas as pd
import numpy as np
from os import path, listdir
import matplotlib.pyplot as plt
import time
import AUC
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier, AdaBoostClassifier, ExtraTreesClassifier, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.svm import NuSVR, OneClassSVM, NuSVC
import sys


def create_submission_file(df):
    """
    Create a submission file for kaggle from a data frame
    """

    # Find file number for new file
    file_num = 0
    while path.isfile('submission-{}.csv'.format(file_num)):
        file_num += 1

    # Write final submission
    df.to_csv('submission-{}.csv'.format(file_num), index = False)


def cross_classify(df_features_driver, df_features_other, nfold):

    df_submission = pd.DataFrame()
    
    df_submission['driver_trip'] = create_first_column(df_features_driver)

    all_probs = []

    for n in range(nfold):
        
        len_fold = int(len(df_features_driver)/nfold)
        ind_train = np.append(np.arange(0,int(n)*len_fold,1),
                              np.arange((int(n)+1)*len_fold,len(df_features_driver),1))
        ind_test = np.arange(int(n)*len_fold,(int(n)+1)*len_fold,1)
        
        df_train = df_features_driver.append(df_features_other)
        df_train.reset_index(inplace = True)
        df_train.Driver = df_train.Driver.astype(int)
        
        df_train = df_features_driver.iloc[ind_train].append(df_features_other.iloc[ind_train])
        df_train.reset_index(inplace = True)
        df_train.Driver = df_train.Driver.astype(int)    
    
        df_test = df_features_driver.iloc[ind_test]
        df_test.reset_index(inplace = True)
        df_test.Driver = df_test.Driver.astype(int)   
    
        model = GradientBoostingClassifier(n_estimators = 200, min_samples_leaf=2)
    
        feature_columns_train= df_train.iloc[:, 4:]
        feature_columns_test= df_test.iloc[:, 4:]
    
        # Train the classifier
        model.fit(feature_columns_train, df_train.Driver)

    
        probs_array = model.predict_proba(feature_columns_test[:]) # Return array with the probability for every driver
        #probs_df = pd.DataFrame(probs_array)
        
        all_probs = np.append(all_probs, np.array(probs_array[:, 1]))
     
    #all_probs_df = pd.DataFrame(all_probs) 
    #print(all_probs_df)
    df_submission['prob'] = all_probs
    
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

	# Features path
    features_path_1 = sys.argv[1]
    features_files_1 = listdir(features_path_1)

    # Get data frame that contains each trip with its features
    features_df_list_1 = [pd.read_hdf(path.join(features_path_1, f), key = 'table') for f in features_files_1]
    feature_df_1 = pd.concat(features_df_list_1)
    
    feature_df = feature_df_1    
    
    feature_df.reset_index(inplace = True)
    df_list = []
    to = time.time()
    
    # k-fold
    nfold = 5

    for i, (_, driver_df) in enumerate(feature_df.groupby('Driver')):
        indeces = np.append(np.arange(i * 200), np.arange((i+1) * 200, len(feature_df)))
        other_trips = indeces[np.random.randint(0, len(indeces) - 1, 200)]
        others = feature_df.iloc[other_trips]
        others.Driver = int(0)

        submission_df = cross_classify(driver_df, others, nfold)
        df_list.append(submission_df)
        if i%100==0:
            print(i, ": ", int(time.time()-to))

    submission_df = pd.concat(df_list)
    create_submission_file(submission_df)


if __name__ == "__main__":
    main()