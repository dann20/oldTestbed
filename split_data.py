from sklearn.model_selection import train_test_split
import pandas as pd
path = 'IoTID20_modified.csv'
dataset = pd.read_csv(path, index_col= False)
dataset1 = dataset.iloc[:610000,:]
dataset2 = dataset.iloc[610000:,:]
traindata, testdata = train_test_split(dataset1, test_size = 0.2, random_state = 1)
dataset2.to_csv('aftertrain_21092020.csv')
# traindata = pd.read_csv('traindata_20092020.csv')
# testdata = pd.read_csv('testdata_200920.csv')
# for i in range(len(traindata)):
#     traindata.at[i,'Label'] = 1 if traindata.at[i,'Label'] == 'Anomaly' else 0
# for i in range(len(testdata)):
    # testdata.at[i,'Label'] = 1 if testdata.at[i,'Label'] == 'Anomaly' else 0
    # if testdata.at[i,'Label'] == 2:
        # testdata.at[i,'Label'] = 0 
traindata.to_csv('traindata_210920.csv')
testdata.to_csv('testdata_210920.csv')


