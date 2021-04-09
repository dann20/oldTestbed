# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 00:19:22 2020

@author: Minh Long
"""
#import things
import numpy as np
import pandas as pd

import tensorflow as tf #tensorflow ban 2.1.0
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Activation
from tensorflow.keras.layers import Dense

traindata = np.array(pd.read_excel('D:/Future Internet Lab/FedAvg_Code/traindata.xlsx', header=None))
testdata = np.array(pd.read_excel('D:/Future Internet Lab/FedAvg_Code/testdata.xlsx', header=None))
X_train = traindata[:,:-1]
y_train = traindata[:,-1:]
X_test = testdata[:,:-1]
y_test = testdata[:,-1:]
numtotal = np.shape(X_train)[0]

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

model = SimpleMLP().build(37,11)

#cac tham so, compile cac model
epochs = 200
learning_rate = 0.01
batch_size = 64
loss='sparse_categorical_crossentropy'
metrics = ['accuracy']
optimizer = tf.keras.optimizers.SGD(learning_rate=learning_rate)
model.compile(loss=loss,optimizer=optimizer,metrics=metrics)

#chay thu
model.fit(X_train, y_train, epochs = epochs, verbose = 1, batch_size = batch_size) #train local

#test model

results = model.evaluate(X_test, y_test)

model.save('modelcentralized.h5') #luu model global