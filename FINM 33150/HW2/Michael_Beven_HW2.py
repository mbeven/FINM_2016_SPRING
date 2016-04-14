# Michael Beven
# University of Chicago - Financial Mathematics
# FINM 33150 - Quantitative Strategies and Regression
# Homework 2

# make plots come up in this window - ipython notebook
# %matplotlib inline

# import packages
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import Quandl

# write the code in a function, which spits out a final dataframe of results
# makes it easier for analysis
def strat(M,g,j,s,X_code,Y_code,X_close,X_volume,Y_close,Y_volume):
  """
  This function creates a dataframe with results to a spread trading strategy
  (see HW2 of FINM 33150 - Quantitative Strategies and Regression)
  Inputs:
  M ~ return difference calculation time frame.  M cannot exceed the number of 
  trading days between 2013-12-02 and 2014-01-01
  g ~ entering threshold
  j ~ exiting threshold
  s ~ stop loss threshold
  X_code ~ Quandl code for X
  Y_code ~ Quandl code for Y
  X_close ~ X column name for close
  X_volume ~ X column name for volume
  Y_close ~ Y column name for close
  Y_volume ~ Y column name for volume
  Example of calling function:
  strat(10,0.01,0.008,0.10,'GOOG/NYSE_XSD','YAHOO/SMH','GOOG.NYSE_XSD - Close',
  'GOOG.NYSE_XSD - Volume','YAHOO.SMH - Close','YAHOO.SMH - Volume')
  """
  ############################################################################
  #2 DATA
  ############################################################################ 
  
  # grab data using Quandl
  raw_data = Quandl.get(list((X_code,Y_code)),authtoken="v21snmSix9KyXBWc1RkF",
      trim_start="2013-12-02",trim_end="2015-12-31",returns="pandas")

  # take a subset of columns of the close data and volume (volume needed for daily
  # dollar volume)
  raw_data_close = pd.DataFrame(raw_data.ix[:,(X_close,X_volume,Y_close,Y_volume)])
  raw_data_close.columns = ['XP','XV','YP','YV']

  # calculate daily dollar volumes
  XSD_DDV = pd.DataFrame(raw_data_close.XP*raw_data_close.XV)
  XSD_DDV.columns = ['XDDV']

  # create 15 day rolling median of data using Pandas
  Nt = pd.DataFrame(pd.rolling_median(XSD_DDV.XDDV,15))
  Nt.columns = ['Nt']
  
  ############################################################################
  #3 EXERCISE
  ############################################################################

  # capital - set K now that we have Nt
  K = np.max(2*Nt.Nt)

  # set up difference calculation of returns based on M previous days.
  # create log return columns and sum over M days.  assumes
  # returns are normally distributed

  # log returns - use the shift technique to calculate
  XR = pd.DataFrame(np.log(raw_data_close['XP']) - np.log(raw_data_close['XP'].shift(1)))
  XR.columns=['XR']
  YR = pd.DataFrame(np.log(raw_data_close['YP']) - np.log(raw_data_close['YP'].shift(1)))
  YR.columns=['YR']

  # difference of X and Y
  Delta = pd.DataFrame(XR.XR-YR.YR)
  Delta.columns=['Delta']

  # previous M day accumulated difference 
  DeltaM = pd.DataFrame(pd.rolling_sum(Delta.Delta,M))
  DeltaM.columns = ['DeltaM']

  # set dataframe and drop the unnecessary month in 2013.  This month
  # is now unnecessary because we have calculated the M day difference.
  df = pd.concat([raw_data_close,XSD_DDV,XR,YR,Delta,DeltaM,Nt],axis=1)
  df = df[df.index >= '2014-01-01'] # drop unnecessary date range

  # add empty signal column - the signal will be our way of telling whether
  # we are entering or maintaining a trade (in this case Signal = 1).
  Signal = pd.DataFrame(np.zeros((len(df),1))).set_index(df.index)
  Signal.columns = ['Signal']

  # beginning January 1 2014, start generating signals based on g/j
  Signal.Signal[np.abs(df.DeltaM) > g] = 1 # should be entering or maintaining trade
  Signal.Signal[np.abs(df.DeltaM) < j] = -1 # should be exiting or out of trade

  # account for exiting trades at the end of each month
  # create empty data frame
  EOM = pd.DataFrame(np.zeros((len(df),1)),columns=['EOM']).set_index(df.index)
  for i in range (1,len(df)):
    # the first trading day can occur on the 1st, 2nd or 3rd day of a month, 
    # which depends on where the weekend falls.  If we are in day 1, 2 or 3,
    # and the previous row is in a day which is different by more than 1 from
    # the current day, then the previous row must be the last trading day of
    # the previous month.  
    if ((df.index.day[i] <= 3) and (df.index.day[i]-df.index.day[i-1] != 1)):
      Signal.Signal[i-1] = -1 #update Signal
      EOM.EOM[i-1] = 1 #update end of month (EOM)

  for i in range(1,len(df)):
    if Signal.Signal[i] == 0:# this is where  we are between g and j; a trade is either
      #being maintained or we are out of a trade
      Signal.Signal[i] = Signal.Signal[i-1] # fill in where  Signal = 0 (will already be
      # entered or exited from a trade)
  Signal.Signal[Signal.Signal == -1] = 0 # represent exiting trades with 0 instead of -1

      
  # GTC (gross traded cash)
  # for GTC, we need to find where the entry point is and what GTC is at that
  # point, and then track the trade for the whole time that it is maintained.
  # the GTC value is the same (|$long|+|$short| at position entry time) while
  # the trade is on.  A 1/0 indicator is used to keep track of where entry
  # points are, these are then set as the GTC and populated for the trade
  # period.
  GTC = pd.DataFrame(np.zeros((len(df),1)))
  GTC = GTC.set_index(df.index)
  GTC.columns = ['GTC']
  GTC.GTC.ix[0] = 1*(Signal.Signal.ix[0] == 1) # set the correct first indicator
  # set all other entry time indicators
  GTC.GTC = GTC.GTC + 1*((Signal.Signal == 1) & (Signal.shift(1).Signal == 0)) 
  # mutiply by GTC
  GTC.GTC = GTC.GTC*(np.abs(np.round(df.Nt/100,0)*df.XP)+np.abs(np.round(df.Nt/100,0)*df.YP))
  # populate GTC for the entire trade period
  for i in range(1,len(df)):
    if (GTC.GTC[i-1] != 0) & (Signal.Signal[i] == 1):
      GTC.ix[i] = GTC.ix[i-1]
  # stop loss
  Stop = pd.DataFrame(np.zeros((len(df),1)))
  Stop = Stop.set_index(df.index)   
  Stop.columns = ['Stop']
  # mark if the simulation experiences a day such that the present position value
  # has lost more than a proportion s. Update Stop column and Signal column
  Stop.Stop[(DeltaM.DeltaM > j) & (GTC.GTC != 0) & (GTC.GTC*s*-1>np.round(Signal.Signal*df.Nt/100,0).shift(1)*-df.Delta)] = 1
  Signal.Signal[(DeltaM.DeltaM > j) & (GTC.GTC != 0) & (GTC.GTC*s*-1>np.round(Signal.Signal*df.Nt/100,0).shift(1)*-df.Delta)] = 0
  Stop.Stop[(DeltaM.DeltaM < j) & (GTC.GTC != 0) & (GTC.GTC*s*-1>np.round(Signal.Signal*df.Nt/100,0).shift(1)*df.Delta)] = 1
  Signal.Signal[(DeltaM.DeltaM < j) & (GTC.GTC != 0) & (GTC.GTC*s*-1>np.round(Signal.Signal*df.Nt/100,0).shift(1)*df.Delta)] = 0


  # roll forward the stop until DeltaM is above g again
  for i in range(1,len(df)):
    if ((Stop.Stop[i-1]==1) | (Signal.Signal[i-1]==-1)) & (np.abs(df.DeltaM[i]) < g):
        Signal.Signal[i] = -1
        Stop.Stop[i] = 0
  Signal.Signal[Signal.Signal == -1] = 0 # represent exiting trades with 0 instead of -1

  # add empty columns for entry and exit points
  Entry = pd.DataFrame(np.zeros((len(df),1)))
  Entry = Entry.set_index(df.index)
  Entry.columns = ['Entry']
  Exit = pd.DataFrame(np.zeros((len(df),1)))
  Exit = Exit.set_index(df.index)
  Exit.columns = ['Exit']

  # create entry and exit points
  Entry.Entry.ix[0] = (Signal.Signal.ix[0] == 1) # set first day of trading
  Entry.Entry = Entry.Entry + 1*((Signal.Signal == 1) & (Signal.shift(1).Signal == 0))
  Exit.Exit.ix[0] = False # cannot exit on the first day
  Exit.Exit = Exit.Exit + 1*((Signal.Signal == 0) & Signal.shift(1).Signal == 1)

  # make the trade
  Size = pd.DataFrame(np.round(Signal.Signal*df.Nt/100,0)) # size of trade
  Size.columns = ['Size']
  # the dollar profit(loss) is going to be the next day after the  trade has been
  # entered.  this profit amount will be the difference in returns of X and Y
  # times the trade size
  Profit = pd.DataFrame(np.zeros((len(df),1)))
  Profit = Profit.set_index(df.index)
  Profit.columns = ['Profit']
  for i in range(1,len(df)):
      if DeltaM.DeltaM[i] > j:
          Profit.Profit[i] = Size.Size[i-1]*(-df.Delta[i])
      if DeltaM.DeltaM[i] < j:
          Profit.Profit[i] = Size.Size[i-1]*(df.Delta[i])
  Profit.ix[0] = 0 # can't calculate profit for the first day
  Cum_Profit = pd.DataFrame(np.cumsum(Profit.Profit)) #cumulative profit
  Cum_Profit.columns = ['Cum_Profit']
  # capital - the capital available grows(shrinks) on a daily basis, based on
  # the amount we have profited(lost)
  K = pd.DataFrame(np.round(K + Cum_Profit.Cum_Profit,0))
  K.columns = ['K']
  Cum_Return = pd.DataFrame(K.K/K.K[0]-1)
  Cum_Return.columns = ['Cum_Return']

  # set dataframe - make it easier to read and in one table for outputting
  df =  pd.concat([df.XP,df.XV,np.round(df.XDDV,0),np.round(df.YP,2),df.YV,np.round(df.Nt,0),np.round(df.XR,3), 
                   np.round(df.YR,3),np.round(df.Delta,3),np.round(df.DeltaM,3),Signal,Entry,Exit,
                  EOM,Size,np.round(GTC,0),Stop,np.round(Profit,0),np.round(Cum_Profit,0),K,
                  Cum_Return],
                  axis=1)
  return df

# output
M = 20
G = 0.0014
J = 0.0002
s = 0.00009
X_code = 'EOD/XSD'
Y_code = 'EOD/SMH'
X_close = 'EOD.XSD - Adj_Close'
X_volume = 'EOD.XSD - Adj_Volume'
Y_close = 'EOD.SMH - Adj_Close'
Y_volume = 'EOD.SMH - Adj_Volume'
df = strat(M,G*M,J*M,s,X_code,Y_code,X_close,X_volume,Y_close,Y_volume)  

# let's see what comes out
pd.set_option('display.max_columns', 500)
print(df[(df.index.year == 2014) & (df.index.month == 1)])
print(df[(df.index.year == 2015) & (df.index.month == 12)])

# plot DeltaM with entry and exit points
plt.figure(1,figsize=(16,8))
plt.title('Difference in Returns Over M Days')
plt.ylabel('Return Difference')
df.DeltaM.plot(color='black')
plt.axhline(y=G*M,color='green')
plt.axhline(y=J*M,color='red')
plt.axhline(y=-G*M,color='green')
plt.axhline(y=-J*M,color='red')
Entry_Pts = pd.DataFrame(df.Entry*df.DeltaM)
Entry_Pts = Entry_Pts[Entry_Pts != 0]
Exit_Pts = pd.DataFrame(df.Exit*df.DeltaM)
Exit_Pts = Exit_Pts[Exit_Pts != 0]
Stop_Pts = pd.DataFrame(df.Stop*df.DeltaM)
Stop_Pts = Stop_Pts[Stop_Pts != 0]
p1, = plt.plot(Entry_Pts,'g.')
p2, = plt.plot(Exit_Pts,'r.')
p3, = plt.plot(Stop_Pts,'r*',ms=10)
for i in range(0,len(df)):
    if df.EOM[i] == 1:
        plt.axvline(x=df.index[i],color='grey')
plt.legend([p1,p2,p3],['Entry Point','Exit Point','Stop-Loss Point'],
           numpoints=1,loc='lower right')

# plot cumulative profit
plt.figure(2,figsize=(16,8))
plt.title('Cumulative Profit')
plt.ylabel('Dollar Profit')
df.Cum_Profit.plot(color='black')
Entry_Pts = pd.DataFrame(df.Entry*df.Cum_Profit)
Entry_Pts = Entry_Pts[Entry_Pts != 0]
Exit_Pts = pd.DataFrame(df.Exit*df.Cum_Profit)
Exit_Pts = Exit_Pts[Exit_Pts != 0]
Stop_Pts = pd.DataFrame(df.Stop*df.Cum_Profit)
Stop_Pts = Stop_Pts[Stop_Pts != 0]
p1, = plt.plot(Entry_Pts,'g.')
p2, = plt.plot(Exit_Pts,'r.')
p3, = plt.plot(Stop_Pts,'r*',ms=10)
for i in range(0,len(df)):
    if df.EOM[i] == 1:
        plt.axvline(x=df.index[i],color='grey')
plt.legend([p1,p2,p3],['Entry Point','Exit Point','Stop-Loss Point'],
           numpoints=1,loc='lower right')

############################################################################
#4 ANALYSIS
############################################################################

# check overall profit when varying M. need to make j g and s functions of M
Perform_M = pd.DataFrame(columns = ['M','Cum_Profit'])
G = 0.0014
J = 0.0002
s = 0.00009
X_code = 'EOD/XSD'
Y_code = 'EOD/SMH'
X_close = 'EOD.XSD - Adj_Close'
X_volume = 'EOD.XSD - Adj_Volume'
Y_close = 'EOD.SMH - Adj_Close'
Y_volume = 'EOD.SMH - Adj_Volume'
for M in range(1,25):
  df = strat(M,G*M,J*M,s,X_code,Y_code,X_close,X_volume,Y_close,Y_volume)
  Perform_M = Perform_M.append(pd.DataFrame([[M,df.Cum_Profit[-1]]],columns=['M','Cum_Profit']),
      ignore_index=True)
plt.figure(3)
plt.plot(Perform_M.M,Perform_M.Cum_Profit,color='black') # M=12 looks optimal
plt.title('Profit When Varying M')
plt.ylabel('Total Profit (dollars)')
plt.xlabel('M (days)')
plt.grid()

# check overall profit when widening the spread of g and j
Perform_W = pd.DataFrame(columns = ['W','Cum_Profit'])
M = 20
s = 0.00009
X_code = 'EOD/XSD'
Y_code = 'EOD/SMH'
X_close = 'EOD.XSD - Adj_Close'
X_volume = 'EOD.XSD - Adj_Volume'
Y_close = 'EOD.SMH - Adj_Close'
Y_volume = 'EOD.SMH - Adj_Volume'
for i in range(0,14):
  i = i/10000
  #G = 0.0012+i
  G = 0.0014
  J = 0.0014-i
  df = strat(M,G*M,J*M,s,X_code,Y_code,X_close,X_volume,Y_close,Y_volume)
  Perform_W = Perform_W.append(pd.DataFrame([[G,J,G-J,df.Cum_Profit[-1]]],columns=['G','J','W','Cum_Profit']),
      ignore_index=True)
plt.figure(4)
plt.plot(Perform_W.W,Perform_W.Cum_Profit,color='black') # window of 0.0011 looks good
plt.title('Profit When Widening the Spread of G and J')
plt.ylabel('Total Profit (dollars)')
plt.xlabel('G-J')
plt.grid()

# check overall profit when shifting the spread of g and j
Perform_S = pd.DataFrame(columns = ['G','J','Cum_Profit'])
M = 20
s = 0.00009
X_code = 'EOD/XSD'
Y_code = 'EOD/SMH'
X_close = 'EOD.XSD - Adj_Close'
X_volume = 'EOD.XSD - Adj_Volume'
Y_close = 'EOD.SMH - Adj_Close'
Y_volume = 'EOD.SMH - Adj_Volume'
for i in range(0,20):
  i = i/10000
  G = 0.0012+i
  J = 0.0000+i
  df = strat(M,G*M,J*M,s,X_code,Y_code,X_close,X_volume,Y_close,Y_volume)
  Perform_S = Perform_S.append(pd.DataFrame([[G,J,df.Cum_Profit[-1]]],
                                            columns=['G','J','Cum_Profit']),ignore_index=True)
plt.figure(5)
plt.plot((Perform_S.G+Perform_S.J)/2,Perform_S.Cum_Profit,color='black') # window of 0.005 looks good
plt.title('Profit When Shifting the Spread of G and J')
plt.ylabel('Total Profit (dollars)')
plt.xlabel('Midpoint of G and J')
plt.grid()

# check overall profit when varying the stop loss level
Perform_SL = pd.DataFrame(columns = ['s','Cum_Profit'])
M = 20
G = 0.0014
J = 0.0002
X_code = 'EOD/XSD'
Y_code = 'EOD/SMH'
X_close = 'EOD.XSD - Adj_Close'
X_volume = 'EOD.XSD - Adj_Volume'
Y_close = 'EOD.SMH - Adj_Close'
Y_volume = 'EOD.SMH - Adj_Volume'
for s in range(0,40):
  s = s/100000
  df = strat(M,G*M,J*M,s,X_code,Y_code,X_close,X_volume,Y_close,Y_volume)
  Perform_SL = Perform_SL.append(pd.DataFrame([[s,df.Cum_Profit[-1]]],
                                            columns=['s','Cum_Profit']),ignore_index=True)
plt.figure(6)
plt.plot(Perform_SL.s,Perform_SL.Cum_Profit,color='black') # window of 0.0004 looks good
plt.title('Profit When Shifting the Stop Loss Level')
plt.ylabel('Total Profit (dollars)')
plt.xlabel('s')
plt.grid()
