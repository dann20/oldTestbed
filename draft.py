# %%
import pandas as pd
import numpy as np
NUM_LAYER = 3
file = 'aftertrain_200920.csv'
testdata = pd.read_csv(file, usecols= ['Flow_Duration', 'Fwd_Pkt_Len_Max','Idle_Max', 'Flow_IAT_Max', 'Fwd_Pkt_Len_Mean'])
test_labels = pd.read_csv(file, usecols= ['Label'])

W = []
b = []
for i in range(NUM_LAYER):
    W.append(np.loadtxt('mlpcoefs{0}{1}.csv'.format(i + 1,i + 2),delimiter=','))
    k = np.loadtxt('mlpbias{0}{1}.csv'.format(i + 1, i + 2), delimiter=',')
    k = k.reshape((k.shape[0],1)) if k.shape != () else k.reshape((1,1))
    b.append(k)

# %%
A = [testdata.to_numpy()]

# %%
for i in range(NUM_LAYER):
    A.append(A[i].dot(W[i]) + b[i].reshape((b[i].shape[0],)))
    A[-1] = np.maximum(0, A[-1])
test_labels = test_labels.to_numpy()
print(np.mean(np.expand_dims(np.argmax(A[-1],axis=1),1) == test_labels))
# print(np.mean(np.argmax(A[-1],axis=1) == test_labels))
