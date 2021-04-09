from sklearn.neural_network import MLPClassifier
import pandas as pd
import numpy as np
import pickle

col_names = ['TotLen_Bwd_Pkts','Subflow_Bwd_Byts', 'Flow_Duration', 'Init_Bwd_Win_Byts', 'Pkt_Len_Mean']
# traindata = pd.read_csv('traindata_210920.csv', index_col=False, usecols= ['Flow_Duration', 'Fwd_Pkt_Len_Max', 'Idle_Max', 'Flow_IAT_Max', 'Fwd_Pkt_Len_Mean'])
# testdata = pd.read_csv('testdata_210920.csv', index_col=False, usecols=['Flow_Duration', 'Fwd_Pkt_Len_Max', 'Idle_Max', 'Flow_IAT_Max', 'Fwd_Pkt_Len_Mean'])
traindata = pd.read_csv('traindata_210920.csv', index_col=False, usecols= col_names)
testdata = pd.read_csv('testdata_210920.csv', index_col=False, usecols=col_names)
# traindata[:] = np.nan_to_num(traindata)
# testdata[:] = np.nan_to_num(testdata) #replace nan with 0 and inf with large number
train_labels = pd.read_csv('traindata_210920.csv',index_col=False,  usecols= ['Sub_Cat'])
test_labels = pd.read_csv('testdata_210920.csv', index_col=False, usecols= ['Sub_Cat'])
mlp = MLPClassifier(hidden_layer_sizes=(20,15,12), activation='relu', solver='adam', max_iter=1000)
# print(test_labels.shape)
mlp.fit(traindata, train_labels)
print(mlp.score(testdata,test_labels))
# print(mlp.predict(testdata))

# print(f'n_layers = {mlp.n_layers_}')
# print(f'coef_ = {mlp.coefs_}')
# print(f'intercepts_ = {mlp.intercepts_}')
file = 'mlp.sav'

pickle.dump(mlp, open(file,'wb'))

for i in range(len(mlp.coefs_)):
    np.savetxt('mlpcoefs{0}{1}.csv'.format(i + 1,i + 2),mlp.coefs_[i],delimiter=",")
    np.savetxt('mlpbias{0}{1}.csv'.format(i + 1, i + 2), mlp.intercepts_[i],delimiter=",")