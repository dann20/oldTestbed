import pandas as pd 
file = '/home/dann/IoTID20.csv'
dataset = pd.read_csv(file, index_col= False)
for i in range(len(dataset)):
    if dataset.at[i, 'Sub_Cat'] == 'Normal': dataset.at[i, 'Sub_Cat'] = 0
    elif dataset.at[i, 'Sub_Cat'] == 'Mirai-Hostbruteforceg': dataset.at[i, 'Sub_Cat'] = 2
    elif dataset.at[i, 'Sub_Cat'] == 'DoS-Synflooding': dataset.at[i, 'Sub_Cat'] =3
    elif dataset.at[i, 'Sub_Cat'] =='Mirai-HTTP Flooding': dataset.at[i, 'Sub_Cat'] = 4
    elif dataset.at[i, 'Sub_Cat'] == 'Mirai-Ackflooding': dataset.at[i, 'Sub_Cat'] = 5
    elif dataset.at[i, 'Sub_Cat'] == 'Scan Port OS': dataset.at[i, 'Sub_Cat'] = 6
    elif dataset.at[i, 'Sub_Cat'] == 'MITM ARP Spoofing': dataset.at[i, 'Sub_Cat'] = 7
    elif dataset.at[i, 'Sub_Cat'] == 'Scan Hostport': dataset.at[i, 'Sub_Cat'] =8
    else: dataset.at[i, 'Sub_Cat'] = 1
dataset.to_csv('IoTID20_modified.csv')