
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- Project: lucidmode                                                                                  -- #
# -- Description: A Lightweight Framework with Transparent and Interpretable Machine Learning Models     -- #
# -- experiments.py: python script with experiment cases                                                 -- #
# -- Author: IFFranciscoME - if.francisco.me@gmail.com                                                   -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- Repository: https://github.com/lucidmode/lucidmode                                                  -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# -- load class
from lucidmode.models import NeuralNet

# -- load datasets
from tools.io_data import datasets

# -- base libraries
import numpy as np

# -- complementary tools
from rich import inspect
from tools.metrics import metrics
from tools.processing import train_val_split, gridsearch

# ------------------------------------------------------------------------------------- IMAGE CLASSIFIER -- #
# --------------------------------------------------------------------------------------------------------- #

# load example data 
data = datasets('fashion_MNIST')
labels = data['labels']
images = data['images']

# split data
X_train, X_val, y_train, y_val = train_val_split(images, labels, train_size = 0.3, random_state = 1)

# -- Train dataset: X_train.shape(16800, 784) y_train.shape(16800,)
# -- Test dataset: X_test.shape(7200, 784) y_test.shape(7200,)

# Neural Net Topology Definition
lucid = NeuralNet(hidden_l=[30, 30, 10], hidden_a=['tanh', 'sigmoid', 'relu'],
                  hidden_r=[{'type': 'l2', 'lmbda': 0.01, 'ratio':0.1},
                            {'type': 'l1', 'lmbda': 0.001, 'ratio':0.1},
                            {'type': 'l1', 'lmbda': 0.001, 'ratio':0.1}],
                  
                  output_r={'type': 'elasticnet', 'lmbda': 0.001, 'ratio':0.5},
                  output_n=10, output_a='softmax')

# Model and implementation case Formation
lucid.formation(cost={'function': 'multi-logloss'},
                init={'input_shape': X_train.shape[1], 'init_layers': 'xavier-uniform'},
                optimizer={'type': 'SGD', 'params': {'learning_rate': 0.001, 'batch_size': 0}},
                metrics=['acc'])

# Inspect object contents  (Weights initialization)
inspect(lucid)

# cost evolution
lucid.fit(x_train=X_train, y_train=y_train, x_val=X_val, y_val=y_val, epochs=500, verbosity=3)

# acces to the train history information
history = lucid.history

# Predict train
y_hat = lucid.predict(x_train=X_train)
train_metrics = metrics(y_train, y_hat, type='classification')

# Confusion matrix
train_metrics['cm']

# Overall accuracy
train_metrics['acc']

# Predict train
y_val_hat = lucid.predict(x_train=X_val)
val_metrics = metrics(y_val, y_val_hat, type='classification')

# Overall accuracy
val_metrics['acc']

# ----------------------------------------------------------------------- RANDOM GRID SEARCH WITH MEMORY -- # 

# -- Quick tests with less samples
X_train = X_train[0:1000, :]
y_train = y_train[0:1000]
X_val = X_val[0:1000, :]
y_val = y_val[0:1000]

es_callback = {'earlyStopping': {'metric': 'acc', 'threshold': 0.70}}

ds = gridsearch(lucid, X_train, y_train, X_val, y_val,
                es_call=es_callback, metric_goal=0.70, fit_epochs=100, grid_iterations=10)
