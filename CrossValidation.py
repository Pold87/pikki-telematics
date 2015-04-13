from __future__ import division
import pandas as pd
import numpy as np

import AUC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
import multiprocessing as mp
import sys


def crossvalidation(df_features_driver, df_features_other, nfold, model):

    """
    Perform the cross validation for one driver 
    """

    df_auc = []

    for n in range(nfold):

        len_fold = int(len(df_features_driver)/nfold)
        ind_train = np.append(np.arange(0, int(n) * len_fold, 1),
                              np.arange((int(n)+1) * len_fold,
                                        len(df_features_driver), 1))

        ind_test = np.arange(int(n) * len_fold,(int(n) + 1) * len_fold, 1)

        df_train = df_features_driver.iloc[ind_train].append(
            df_features_other.iloc[ind_train])
        df_train.reset_index(inplace=True)
        df_train.Driver = df_train.Driver.astype(int)

        df_test = df_features_driver.iloc[ind_test].append(
            df_features_other.iloc[ind_test])
        df_test.reset_index(inplace=True)
        df_test.Driver = df_test.Driver.astype(int)

        feature_columns_train= df_train.iloc[:, 4:-1]
        feature_columns_test= df_test.iloc[:, 4:-1]

        # Train the classifier
        model.fit(feature_columns_train, df_train.Driver)

        # Measurements for the general model performance
        # print('oob_score', model.oob_score_)
        #print(feature_columns_train.columns.values)
        #fw = zip(feature_columns_train.columns.values, model.feature_importances_)
        #fw.sort(key = operator.itemgetter(1))
        #print(fw)


        # Return array with the probability for every driver
        probs_array = model.predict_proba(feature_columns_test)
        probs_df = pd.DataFrame(probs_array)

        probs_list = np.array(['1', probs_df.ix[0, 1]])

        for x in range(1, len_fold):
            # Column 1 should contain the driver of interest
            probs_list = np.vstack((probs_list, ['1', probs_df.ix[x, 1]]))
        for x in range(len_fold,2 * len_fold):
            # Column 1 should contain the driver of interest
            probs_list = np.vstack((probs_list, ['0', probs_df.ix[x, 1]]))

        df_auc.append(AUC.AUC(probs_list))

    return np.mean(np.array(df_auc))


def validate(f, df_list, nfold, model):

    feature_df = pd.read_hdf("/scratch/vstrobel/features_opti_32/" + f, key = 'table')
    feature_df.reset_index(inplace = True)

    for i, (driver, driver_df) in enumerate(feature_df.groupby('Driver')):

        indeces = np.append(np.arange(0, int(i)*200, 1),
                            np.arange((int(i)+1) * 200, len(feature_df), 1))

        # Get 200 other trips
        other_trips = indeces[np.random.randint(0, len(indeces) - 1, 200)]

        others = feature_df.iloc[other_trips]

        others.Driver = int(0)

        driver_df.Driver = int(1)

        crossvalidation_df = crossvalidation(driver_df, others, nfold, model)
        df_list.append(crossvalidation_df)

def main():

    # Get data frame that contains each trip with its features
    features_path = sys.argv[1]
    features_files = listdir(features_path)

    nfold = 5 # either 2, 4, 5, 10, or 20

    model1 = RandomForestClassifier(n_estimators=10)
    model2 = RandomForestClassifier(1000, min_samples_leaf = 2, min_samples_split = 1)
    # model2 = RandomForestClassifier(1000, n_jobs=-1, min_samples_leaf = 2, min_samples_split = 2)
    # model3 = RandomForestClassifier(1000, n_jobs=-1, min_samples_leaf = 2, min_samples_split = 3)
    # model4 = RandomForestClassifier(1000, n_jobs=-1, min_samples_leaf = 2, min_samples_split = 4)
    # model1 = RandomForestClassifier(500, min_samples_leaf = 3, max_features = 0.5)
    model1 = RandomForestClassifier(100, min_samples_leaf = 2, criterion = 'entropy', max_features = 0.7)
    models = [model1,
              model2]

    for model in models:

        print("New Model", model)
        manager = mp.Manager()
        df_list = manager.list()

        jobs = []

        for f in features_files:
            p = mp.Process(target = validate, args = (f, df_list, nfold, model, ))
            jobs.append(p)
            p.start()

        [job.join() for job in jobs]

        final_list = []

        for l in df_list:
            final_list.append(l)

        final_arr = np.array(final_list)
        print(final_arr.mean())

if __name__ == "__main__":
    main()
