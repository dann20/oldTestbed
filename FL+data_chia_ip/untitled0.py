# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 18:37:53 2020

@author: Minh Long
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import minmax_scale
from sklearn.utils import shuffle

pd2 = pd.read_excel('book2.xlsx')
data2 = pd2
data2 = data2.drop(columns = ['pkSeqID','flgs','proto','saddr','daddr','state','attack','category','subcategory','label'])
scaled_data2 = minmax_scale(data2)
pdscaled = pd.DataFrame(scaled_data2)
pdscaled['label'] = pd2['label']
pdscaled['saddr'] = pd2['saddr']
pdscaled = shuffle(pdscaled)
pdscaled['saddr'] = np.where((pdscaled['saddr']==192168100147),'192.168.100.147',pdscaled['saddr'])
pdscaled['saddr'] = np.where((pdscaled['saddr']==192168100148),'192.168.100.148',pdscaled['saddr'])
pdscaled['saddr'] = np.where((pdscaled['saddr']==192168100149),'192.168.100.149',pdscaled['saddr'])
pdscaled['saddr'] = np.where((pdscaled['saddr']==192168100150),'192.168.100.150',pdscaled['saddr'])
pdscaled.to_excel('output2.xlsx')