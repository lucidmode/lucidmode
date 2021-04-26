
"""
# -- --------------------------------------------------------------------------------------------------- -- #
# -- Project: LucidNet                                                                                   -- #
# -- Description: A Lightweight Framework for Transparent and Interpretable FeedForward Neural Net       -- #
# -- experiments.py: python script with experiment cases                                                 -- #
# -- Author: IFFranciscoME - if.francisco.me@gmail.com                                                   -- #
# -- license: GPL-3.0 License                                                                            -- #
# -- Repository: https://github.com/IFFranciscoME/LucidNet                                               -- #
# -- --------------------------------------------------------------------------------------------------- -- #
"""

# -- load class
from models import Sequential

# -- load datasets
from data import datasets

# -- complementary tools
from rich import inspect

from functions import cost

# ---------------------------------------------------------------------------- OHLC TS BINARY CLASSIFIER -- #
# --------------------------------------------------------------------------------------------------------- #

# ----------------------------------------------------------------------------------- OHLC TS REGRESSION -- #
# --------------------------------------------------------------------------------------------------------- #

# Neural Net Topology Definition
lucid = Sequential(hidden_l=[2], hidden_a=['sigmoid'], output_n=1, output_a='sigmoid')

# load example data
data = datasets('xor')
X, y = data['x'], data['y']

# initialize weights
lucid.init_weights(input_shape=data['x'].shape[1], init_layers=['xavier-standard'])

# Inspect object contents
inspect(lucid)

# cost evolution
J = lucid.fit(data, 1000, 0.1)

# Inspect object contents
inspect(lucid)

# plot cost evolution
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('seaborn-whitegrid')
plt.figure(figsize=(16, 4))
plt.plot(list(J.keys()), list(J.values()), color='r', linewidth=3)
plt.title('Cost over epochs')
plt.xlabel('epochs')
plt.ylabel('cost');
plt.show()


