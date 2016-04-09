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
import Quandl

script = sys.argv

print('Script/file name: {}' .format(script))

# add memoization cache
#@functools.lru_cache(maxsize=20)

# set parameters
M = 10 # return difference calculation time frame. 
#M cannot exceed the number of trading days between 2013-12-02 and 2014-01-01
g = 0.01 # entering threshold
j = 0.008 # exiting threshold
s = 0.10 # stop loss

# grab data
raw_data = Quandl.get(list(('GOOG/NYSE_XSD','YAHOO/SMH')),
    authtoken="v21snmSix9KyXBWc1RkF",
    trim_start="2013-12-02",
    trim_end="2015-12-31",
    returns="pandas")
print(pd.DataFrame(raw_data.columns))

# take a subset of columns of the close data and volume (volume needed for daily
# dollar volume)
raw_data_close = pd.DataFrame(raw_data.ix[:,('GOOG.NYSE_XSD - Close',
                                'GOOG.NYSE_XSD - Volume',
                                'YAHOO.SMH - Close',
                                'YAHOO.SMH - Volume')])
raw_data_close.columns = ['XP','XV','YP','YV']

# calculate daily dollar volumes
XSD_DDV = pd.DataFrame(raw_data_close.loc[:,'XP']*raw_data_close.loc[:,'XV']
, columns=['XDDV'])

# set dataframe - join on daily dollar volumes
df = pd.concat([raw_data_close,XSD_DDV],axis=1)

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
# returns are normally distributed

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

# beginning January 1 2014, start generating signals based on g/j
Signal.Signal[df.DeltaM > g] = 1 # enter trade
Signal.Signal[df.DeltaM < j] = -1 # exit trade
for i in range(1,len(df)):
  if Signal.Signal[i] == 0:
    Signal.Signal[i] = Signal.Signal[i-1] # fill in where  Signal = 0 (will already be
    # entered or exited from a trade)
Signal.Signal[Signal.Signal == -1] = 0 # represent exiting trades with 0 instead of -1

# account for exiting trades at the end of each month
for i in range (1,len(df)):
  if ((df.index.day[i] <= 3) & (df.index.day[i]-df.index.day[i-1] != 1)):
    Signal.Signal[i-1] = 0 

# add empty columns for entry and exit points
Entry = pd.DataFrame(np.zeros((len(df),1)))
Entry = Entry.set_index(df.index)
Entry.columns = ['Entry']
Exit = pd.DataFrame(np.zeros((len(df),1)))
Exit = Exit.set_index(df.index)
Exit.columns = ['Exit']

# create entry and exit points
for i in range (0,len(df)):
  if (i == 0) & (Signal.Signal[i] == 1):
    Entry.Entry[i] = 1
  elif (i == 0) & (Signal.Signal[i] == 0):
    Entry.Entry[i] = 0
    Exit.Exit[i] = 0
  else:
    if (Signal.Signal[i] == 1) & (Signal.Signal[i-1] == 0):
      Entry.Entry[i] = 1
    elif (Signal.Signal[i] == 0) & (Signal.Signal[i-1] == 1):
      Exit.Exit[i] = 1

# make the trade
Size = pd.DataFrame(np.round(Signal.Signal*df.Nt/100,0)) # size of trade
Size.columns = ['Size']
GTC = pd.DataFrame(Entry.Entry*(np.abs(Size.Size*df.XP) +
  np.abs(Size.Size*df.XP)),columns=['GTC']) # gross traded cash
for i in range(1,len(df)):
  if (GTC.GTC[i-1] != 0) & (Exit.Exit[i] != 1):
    GTC.ix[i] = GTC.ix[i-1]
GTC.columns = ['GTC']
Profit = pd.DataFrame(Size.Size.shift(1)*(df.Delta)) # dollar profit(loss)
Profit.ix[0] = 0 # can't calculate profit for the first day
Profit.columns = ['Profit']
Cum_Profit = pd.DataFrame(np.cumsum(Profit.Profit))
Cum_Profit.columns = ['Cum_Profit']
K = pd.DataFrame(np.round(K + Cum_Profit.Cum_Profit,0))
K.columns = ['K']
Cum_Return = pd.DataFrame(K.K/K.K[0]-1)
Cum_Return.columns = ['Cum_Return']

# set dataframe
df = pd.concat([df.XP,df.XV,np.round(df.XDDV,0),df.YP,df.YV,np.round(df.Nt,0),np.round(df.XR,3),
                np.round(df.YR,3),np.round(df.Delta,3),np.round(df.DeltaM,3),Signal,Entry,Exit,
                Size,np.round(GTC,0),np.round(Profit,0),np.round(Cum_Profit,0),K,
                Cum_Return],
                axis=1)
                
# plots
                
# plot DeltaM with entry and exit points
plt.figure(1)
plt.title('Difference in Returns Over M Days')
plt.ylabel('Return Difference')
df.DeltaM.plot(color='black')
Entry_Pts = pd.DataFrame(df.Entry*df.DeltaM)
Entry_Pts = Entry_Pts[Entry_Pts != 0]
Exit_Pts = pd.DataFrame(df.Exit*df.DeltaM)
Exit_Pts = Exit_Pts[Exit_Pts != 0]
plt.plot(Entry_Pts,'g.')
plt.plot(Exit_Pts,'r.')

# plot cumulative profit
plt.figure(2)
plt.title('Cumulative Profit')
plt.ylabel('Dollar Profit')
df.Cum_Profit.plot(color='black')
Entry_Pts = pd.DataFrame(df.Entry*df.Cum_Profit)
Entry_Pts = Entry_Pts[Entry_Pts != 0]
Exit_Pts = pd.DataFrame(df.Exit*df.Cum_Profit)
Exit_Pts = Exit_Pts[Exit_Pts != 0]
plt.plot(Entry_Pts,'g.')
plt.plot(Exit_Pts,'r.')
