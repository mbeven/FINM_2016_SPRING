# make plots come up in this window
# %matplotlib inline 

# import packages
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy as sp
from pandas.stats.api import ols
import Quandl
import functools
import seaborn as sns
import ggplot as gg

script = sys.argv

print('Script/file name: {}' .format(script))

# add memorization cache
#@functools.lru_cache(maxsize=20)

# grab data
raw_data = Quandl.get(list(("YAHOO/MSFT","WIKI/BAC")),
    authtoken="v21snmSix9KyXBWc1RkF",
    trim_start="1990-10-15",
    trim_end="1990-11-09",
    returns="pandas")
print(pd.DataFrame(raw_data.columns))

# take a subset of columns of the close data
raw_data_close = raw_data.ix[:,('YAHOO.MSFT - Close','WIKI.BAC - Close')]

# can look through all the columns to see output
print(raw_data_close.ix[:,'YAHOO.MSFT - Close'])
print(raw_data_close.ix[:,'WIKI.BAC - Close'])

# run an OLS regression of MSFT on BAC close prices
regress = ols(y=raw_data_close["YAHOO.MSFT - Close"], x=raw_data_close["WIKI.BAC - Close"])
print(regress)

# calculate log returns on close prices
N = len(raw_data)
log_rets = np.log(raw_data_close) - np.log(raw_data_close.shift(1))
# remove NaN in first row
log_rets = log_rets.ix[1:-1,:]

# run an OLS regression of MSFT on BAC returns
regress_log_rets = ols(y=log_rets["YAHOO.MSFT - Close"], x=log_rets["WIKI.BAC - Close"])
print(regress_log_rets)
