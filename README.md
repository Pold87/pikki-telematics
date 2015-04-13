# Driver Telematics Analysis - Team PIKKI

The code reached an AUC of 0.8850 on the public leaderboard on kaggle
for the [Driver Telematic Analysis
](http://www.kaggle.com/c/axa-driver-telematics-analysis/).

The code is split in three main parts that should be successively
called:

### Step_1_Create_DataFrame.py:

In this step, the entire kaggle data set is read into data frames and
saved in HDF5 files. This step only has to be done once, and reduces
the time required for Step 2 and 3. It is called by 'python
Step_1_Create_DataFrame.py <drivers_path>', where <drivers_path>
denotes the path of the drivers from Kaggle.


### Step_2_Extract_Features.py:

Here, features for each trip are extracted, using the definition of
Features.py, put in a data frame and saved in HDF5 format.
It is called by
'python Step_2_Extract_Features.py <features_path>'

### Step_3_Classify.py:

In this step, a supervised learning approach (Random Forest
Classifier) is used. For this, a classifier is trained for each driver
as positive set and 200 random trips from other drivers are used as
negative training set. It is called by
'python Step_3_Classify.py <features_path>'

## Helper files

- Features.py

Contains the definitions of the 69 features that were
used in the feature extraction step (Step 2).

- Helpers.py

Contains code for creating successive n-sized chunks.

# Additional files

- CrossClassify.py

Contains 'cross-classification' for training the model using
folds. That means it leaves out a certain amount of trips for each
driver (e.g. 40 if #fold = 5) and trains the model on the rest of the
trips (e.g. 160 if #fold = 5). Therefore, the trips that are to be
predicted are not contained in the training set of the model. This
makes it more robust with regard to overfitting. It is called by
'python CrossClassify.py <features_path>'

- CrossValidation.py

Contains the cross-validation that was performed by using random trips
from other drivers and assuming all trips in a driver’s folder to
belong to this driver. It is called by
'python CrossValidation.py <features_path>'

- Repeated_Trips.py

This algorithm compared the Euclidean distances between all
segments of two trips. To this end, in a preprocessing step, a new
representation of the trips was generated using only the points in
time that surpassed a distance threshold, while the intermediate
points were discarded. To account for cut off parts of trips, the
shorter trip was mapped onto the longer trip at each possible starting
segment of the longer trip. The similarity was then defined as the
maximum ratio between the distances below a threshold and the amount
total of segments of the shorter trip.