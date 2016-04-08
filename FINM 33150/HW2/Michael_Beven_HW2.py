# Michael Beven
# University of Chicago - Financial Mathematics
# FINM 33150 - Quantitative Strategies and Regression
# Homework 2

# make plots come up in this window - ipython notebook
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

# set parameters
M = 3 # return difference calculation time frame. 
#M cannot exceed the number of trading days between 2013-12-02 and 2014-01-01
g = 0.02 # entering threshold
j = 0 # exiting threshold

# grab data
raw_data = Quandl.get(list(('GOOG/NYSE_XSD','YAHOO/SMH')),
    authtoken="v21snmSix9KyXBWc1RkF",
    trim_start="2013-12-02",
    trim_end="2015-12-31",
    returns="pandas")
print(pd.DataFrame(raw_data.columns))

# take a subset of columns of the close data and volume (volume needed for daily
# dollar volume)
columns = ['XP','XV','YP','YV']
raw_data_close = pd.DataFrame(raw_data.ix[:,('GOOG.NYSE_XSD - Close',
                                'GOOG.NYSE_XSD - Volume',
                                'YAHOO.SMH - Close',
                                'YAHOO.SMH - Volume')])
raw_data_close.columns = columns

# calculate daily dollar volumes
XSD_DDV = pd.DataFrame(raw_data_close.loc[:,'XP']*raw_data_close.loc[:,'XV']
, columns=['XDDV'])

# join on daily dollar volumes
df = pd.concat([raw_data_close,XSD_DDV],axis=1)

# can look through all the columns to see output
print(df.head())
print(df.tail())

# create 15 day rolling median of data
Nt = pd.DataFrame(np.zeros((len(df),1)))
Nt = Nt.set_index(df.index)
Nt.columns = ['Nt']
for i in range(14,len(df)):
  Nt.ix[i] = np.median(df.ix[i-14:i,'XDDV'])
df = pd.concat([df,Nt],axis=1)

# capital - set K now that we have Nt
K = np.max(2*Nt.Nt)

# set up difference calculation of returns based on M
# create log return columns and sum over M days.  assumes
# returns are lognormally distributed

# log returns
XR = pd.DataFrame(np.log(df['XP']) - np.log(df['XP'].shift(1)))
XR.columns=['XR']
YR = pd.DataFrame(np.log(df['YP']) - np.log(df['YP'].shift(1)))
YR.columns=['YR']

# difference of X and Y
Delta = pd.DataFrame(XR.XR-YR.YR)
Delta.columns=['Delta']

# previous M day difference 
DeltaM = pd.DataFrame(pd.rolling_sum(Delta.Delta,M))
DeltaM.columns = ['DeltaM']

# set dataframe
df = pd.concat([df,XR,YR,Delta,DeltaM],axis=1)
df = df[df.index >= '2014-01-01'] # drop unnecessary date range

# add empty signal column
Signal = pd.DataFrame(np.zeros((len(df),1)))
Signal = Signal.set_index(df.index)
Signal.columns = ['Signal']
df = pd.concat([df,Signal],axis=1)

# beginning January 1 2014, start generating signals based on g/j
df.Signal[df.DeltaM > g] = 1
df.Signal[df.DeltaM < j] = -1
for i in range(1,len(df)):
  if df.Signal[i] == 0:
    df.Signal[i] = df.Signal[i-1]
df.Signal[df.Signal == -1] = 0

# account for end of month
for i in range (1,len(df)):
  if ((df.index.day[i] <= 3) & (df.index.day[i]-df.index.day[i-1] != 1)):
    df.Signal[i-1] = 0

# make the trade
Size = pd.DataFrame(np.round(df.Signal*df.Nt/100,0))
Size.columns = ['Size']
Profit = pd.DataFrame(Size.Size.shift(1)*(df.YR-df.XR))
Profit.ix[0] = 0
Profit.columns = ['Profit']
Cum_Profit = pd.DataFrame(np.cumsum(Profit.Profit))
Cum_Profit.columns = ['Cum_Profit']
K = pd.DataFrame(np.round(K + Cum_Profit.Cum_Profit,0))
K.columns = ['K']
Cum_Return = pd.DataFrame(K.K/K.K[0]-1)
Cum_Return.columns = ['Cum_Return']

# set dataframe
df = pd.concat([df,Size,Profit,Cum_Profit,K,Cum_Return],axis=1)
