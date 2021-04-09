import pandas as pd
import pickle
from sklearn.neural_network import MLPClassifier

load_model = pickle.load(open('mlp.sav', 'rb'))
# num = 0
# while True:
# file = "/home/dann/CICFlowMeter/data/daily/2020-09-18_Flow.csv"
file = 'aftertrain_200920.csv'
# row_count = sum(1 for row in open(file))     
# if num != row_count:
# test_data = pd.read_csv(file, index_col=False, usecols=['Flow Duration', 'Fwd Packet Length Max','Idle Max', 'Flow IAT Max', 'Fwd Packet Length Mean'])
# test_data.columns = ['Flow_Duration', 'Fwd_Pkt_Len_Max','Idle_Max', 'Flow_IAT_Max', 'Fwd_Pkt_Len_Mean']
test_data = pd.read_csv(file, index_col=False, usecols= ['Flow_Duration', 'Fwd_Pkt_Len_Max','Idle_Max', 'Flow_IAT_Max', 'Fwd_Pkt_Len_Mean'])
test_labels = pd.read_csv(file, index_col=False, usecols=['Label'])
print(load_model.predict(test_data))
print(load_model.score(test_data, test_labels))
# num = row_count
# print(num)  
