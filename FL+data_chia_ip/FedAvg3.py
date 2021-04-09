# -*- coding: utf-8 -*-
"""
Created on Sat Aug  8 11:27:50 2020

@author: Minh Long
"""

 #import things
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import tensorflow as tf #tensorflow ban 2.1.0
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Dense


traindata1 = np.array(pd.read_excel('GW1.xlsx', header=None))
traindata2 = np.array(pd.read_excel('GW2.xlsx', header=None))
traindata3 = np.array(pd.read_excel('GW3.xlsx', header=None))
traindata4 = np.array(pd.read_excel('GW4.xlsx', header=None))
testdata = np.array(pd.read_excel('testdata2noip.xlsx', header=None))
X_train1 = traindata1[:,:-1]
y_train1 = traindata1[:,-1:] #client 1 co cac class 0 1 2
X_train2 = traindata2[:,:-1]
y_train2 = traindata2[:,-1:] #client 2 co cac class 3 4 5
X_train3 = traindata3[:,:-1]
y_train3 = traindata3[:,-1:] #client 3 co cac class 6 7 8 9 10
X_train4 = traindata4[:,:-1]
y_train4 = traindata4[:,-1:]
X_test = testdata[:,:-1]
y_test = testdata[:,-1:] #test co du cac class
numtotal = np.shape(X_train1)[0] + np.shape(X_train2)[0] + np.shape(X_train3)[0] + np.shape(X_train4)[0]
weightclient1 = np.shape(X_train1)[0]/numtotal #trong so tung client
weightclient2 = np.shape(X_train2)[0]/numtotal
weightclient3 = np.shape(X_train3)[0]/numtotal
weightclient4 = np.shape(X_train4)[0]/numtotal

#create model
class SimpleMLP:
    @staticmethod
    def build(shape, classes):
        model = Sequential()
        model.add(Dense(20, input_shape=(shape,)))
        model.add(Activation("relu"))
        model.add(Dense(classes))
        model.add(Activation("softmax"))
        return model

model1 = SimpleMLP().build(37,11) #37 features, 11 classes
model2 = SimpleMLP().build(37,11)
model3 = SimpleMLP().build(37,11)
model4 = SimpleMLP().build(37,11)
modelgbl = SimpleMLP().build(37,11)

#cac tham so, compile cac model
comms_round = 2000
local_epoch = 1
learning_rate = 0.01
batch_size = 64
loss='sparse_categorical_crossentropy'
metrics = ['accuracy']
optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)
#optimizer = 'adam'
model1.compile(loss=loss,optimizer=optimizer,metrics=metrics)
model2.compile(loss=loss,optimizer=optimizer,metrics=metrics)
model3.compile(loss=loss,optimizer=optimizer,metrics=metrics)
model4.compile(loss=loss,optimizer=optimizer,metrics=metrics)
modelgbl.compile(loss=loss,optimizer=optimizer,metrics=metrics)
loss_hist = []
acc_hist = []

#chay thu
for i in range(comms_round): #so lan tong hop global
    gblweights = modelgbl.get_weights() #lay weights cua model tong
    model1.set_weights(gblweights) #cac model client lay weight bang model tong
    model2.set_weights(gblweights)
    model3.set_weights(gblweights)
    model4.set_weights(gblweights)
    model1.fit(X_train1, y_train1, epochs = local_epoch, verbose = 0, batch_size = batch_size) #train local
    model2.fit(X_train2, y_train2, epochs = local_epoch, verbose = 0, batch_size = batch_size)
    model3.fit(X_train3, y_train3, epochs = local_epoch, verbose = 0, batch_size = batch_size)
    model4.fit(X_train4, y_train4, epochs = local_epoch, verbose = 0, batch_size = batch_size)
    model1weights = model1.get_weights() #lay weight tung model con
    model2weights = model2.get_weights()
    model3weights = model3.get_weights()
    model4weights = model4.get_weights()
    averageweights = np.multiply(model1weights,weightclient1) + np.multiply(model2weights,weightclient2) \
        + np.multiply(model3weights,weightclient3) + np.multiply(model4weights,weightclient4) #FedAvg
    modelgbl.set_weights(averageweights) #cho model tong bang cai vua tinh duoc
    #test model
    print("global comms round",i+1,":")
    results = modelgbl.evaluate(X_test, y_test)
    loss_hist.append(results[0])
    acc_hist.append(results[1])
plt.figure(1)
plt.clf()
plt.plot(loss_hist)
plt.plot(acc_hist)
plt.show()
#
modelgbl.save('modelgbl.h5') #luu model global

