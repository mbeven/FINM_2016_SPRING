# make plots come up in this window
# %matplotlib inline 

# import packages
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas.stats.api import ols
import Quandl

script = sys.argv

print('Script/file name: {}' .format(script))

# add memorization cache
#@functools.lru_cache(maxsize=20)

# grab data
raw_data = Quandl.get(list(("YAHOO/MSFT","WIKI/BAC")),
    authtoken="v21snmSix9KyXBWc1RkF",
    trim_start="2015-10-15",
    trim_end="2015-11-09",
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

# plot prices regression
x = regress.x['x']
y = regress.beta[0]*x+regress.beta[1]
plt.figure(1)
plt.plot(x,y)
plt.scatter(x,regress.y)
plt.ylabel('YAHOO.MSFT - Close')
plt.xlabel('WIKI.BAC - Close')
plt.title('Regression of Microsoft Close Price on Bank of America Close Price')

# plot returns regression
x = regress_log_rets.x['x']
y = regress_log_rets.beta[0]*x+regress_log_rets.beta[1]
plt.figure(2)
plt.plot(x,y)
plt.scatter(x,regress_log_rets.y)
plt.ylabel('YAHOO.MSFT - Close')
plt.xlabel('WIKI.BAC - Close')
plt.title('Regression of Microsoft Close Return on Bank of America Close Return')



