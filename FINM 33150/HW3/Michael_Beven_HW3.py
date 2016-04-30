# Michael Beven - 455613
# University of Chicago - Financial Mathematics
# FINM 33150 - Quantitative Strategies and Regression
# Homework 3 

# make plots come up in this window - ipython notebook
# %matplotlib inline

# import packages
import pandas as pd
import numpy as np
import Quandl
import keyring
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# set global variables
auth = keyring.get_password('Quandl','mbeven')
start_date = "2013-12-02"
trade_begin = "2014-01-01"
end_date = "2015-12-31"

# reversion strategy function
def strat(M,g,j,X_code,Y_code,X_close,X_volume,Y_close,Y_volume):
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
  # grab data using Quandl
  ETF_data = Quandl.get(list((X_code,Y_code)),authtoken=auth,trim_start=start_date,trim_end=end_date,returns="pandas")
  df = pd.DataFrame(ETF_data.ix[:,(X_close,X_volume,Y_close,Y_volume)]) #subset
  df.columns = ['XP','XV','YP','YV']
  df['XDDV'] = df.XP*df.XV # calculate daily dollar volumes
  df['Nt'] = pd.rolling_median(df.XDDV,15).shift(1)# 15 day rolling median
  K = np.max(2*df.Nt) # capital - set K now that we have Nt
  df['XR'] = np.log(df.XP) - np.log(df.XP.shift(1)) #logrets
  df['YR'] = np.log(df.YP) - np.log(df.YP.shift(1))
  df['Delta'] = df.XR-df.YR # difference of X and Y
  df['DeltaM'] = pd.rolling_sum(df.Delta,M).shift(1) #M day historical accumulated difference 
  df = df[df.index >= trade_begin] # drop unnecessary date range
  df['Signal'] = np.nan # add empty trade signal column
  df.Signal[df.DeltaM > g] = 1 # entering or maintaining trade
  df.Signal[df.DeltaM < -g] = -1 # entering or maintaining trade
  df.Signal[np.abs(df.DeltaM) < j] = 0 # exiting or out of trade
  df['EOM'] = np.nan # end of month
  df.EOM[(df.shift(1,freq='B').index.day <= 3) & (df.shift(1,freq='B').index.day-df.index.day < -1)] = 1 # day before 1st day
  df.Signal[(df.shift(1,freq='B').index.day <= 3) & (df.shift(1,freq='B').index.day-df.index.day < -1)] = 0
  df.Signal[((df.Signal == -1) & (df.DeltaM > j)) | (df.Signal == 1) & (df.DeltaM < j)] = 0
  for i in range(1,len(df)):
    if np.isnan(df.Signal[i]):# if between g and j
      df.Signal[i] = df.Signal[i-1] # fill in with current position
  df['Entry'] = 1*(((df.Signal == 1) | (df.Signal == -1)) & ((df.shift(1).Signal == 0) | (np.isnan(df.shift(1).Signal) == True))) # entry point
  df.Entry[((df.Signal == -1) & (df.shift(1).Signal == 1)) | ((df.Signal == 1) & (df.shift(1).Signal == -1))] = 1 # jumping g to -g or vice versa
  df['Exit'] = 1*((df.Signal == 0) & ((df.shift(1).Signal == 1) | ((df.shift(1).Signal == -1)))) # exit point
  df['Nx'] = np.round(-df.Signal*df.Nt/100/df.XP,0) # size of X trade
  df['Ny'] = np.round(df.Signal*df.Nt/100/df.YP,0) # size of Y trade
  df['Profit'] = pd.DataFrame((df.Nx.shift(1)*df.XP.shift(1)*df.XR)+df.Ny.shift(1)*df.YP.shift(1)*df.YR) # dollar profit(loss)
  df['Cum_Profit'] = np.cumsum(df.Profit) #cumulative profit
  df['K'] = np.round(K + df.Cum_Profit,0) # capital based on changes in profit  
  df['Return'] = 252*df.Profit/df.K.shift(1) # annualised returns  
  return df

# set up a dataframe of the simulations to run
sims = pd.DataFrame(columns=['M','g','j','X_code','Y_code','X_close','X_volume','Y_close','Y_volume'])
sims.loc[0] = [20,0.02,0.005,'EOD/RYU','EOD/XLU','EOD.RYU - Adj_Close','EOD.RYU - Adj_Volume','EOD.XLU - Adj_Close','EOD.XLU - Adj_Volume']
sims.loc[1] = [20,0.060,0.028,'EOD/IST','EOD/IYZ','EOD.IST - Adj_Close','EOD.IST - Adj_Volume','EOD.IYZ - Adj_Close','EOD.IYZ - Adj_Volume']
sims.loc[2] = [20,0.021,0.016,'EOD/RING','EOD/GDX','EOD.RING - Adj_Close','EOD.RING - Adj_Volume','EOD.GDX - Adj_Close','EOD.GDX - Adj_Volume']
sims.loc[3] = [20,0.05,0.048,'EOD/XSD','EOD/SMH','EOD.XSD - Adj_Close','EOD.XSD - Adj_Volume','EOD.SMH - Adj_Close','EOD.SMH - Adj_Volume']
sims.loc[4] = [20,0.05,0.036,'EOD/PBE','EOD/XBI','EOD.PBE - Adj_Close','EOD.PBE - Adj_Volume','EOD.XBI - Adj_Close','EOD.XBI - Adj_Volume']
sims.loc[5] = [20,0.025,0.006,'EOD/PXJ','EOD/OIH','EOD.PXJ - Adj_Close','EOD.PXJ - Adj_Volume','EOD.OIH - Adj_Close','EOD.OIH - Adj_Volume']
sims.loc[6] = [20,0.07,0.064,'EOD/IEO','EOD/XOP','EOD.IEO - Adj_Close','EOD.IEO - Adj_Volume','EOD.XOP - Adj_Close','EOD.XOP - Adj_Volume']
sims.loc[7] = [20,0.038,0.012,'EOD/RTH','EOD/XRT','EOD.RTH - Adj_Close','EOD.RTH - Adj_Volume','EOD.XRT - Adj_Close','EOD.XRT - Adj_Volume']
sims.loc[8] = [20,0.002,0.0003,'EOD/SIVR','EOD/SLV','EOD.SIVR - Adj_Close','EOD.SIVR - Adj_Volume','EOD.SLV - Adj_Close','EOD.SLV - Adj_Volume']
sims.loc[9] = [20,0.08,0.078,'EOD/HYLD','EOD/JNK','EOD.HYLD - Adj_Close','EOD.HYLD - Adj_Volume','EOD.JNK - Adj_Close','EOD.JNK - Adj_Volume']
sims = sims.set_index(np.array(['ETF0','ETF1','ETF2','ETF3','ETF4','ETF5','ETF6','ETF7','ETF8','ETF9']))
print(sims)

# create all data frames
dfs = {}
for i in range(0,len(sims)):
  dfs['df'+str(i)] = strat(sims.ix[i,'M'],sims.ix[i,'g'],sims.ix[i,'j'],sims.ix[i,'X_code'],sims.ix[i,'Y_code'],sims.ix[i,'X_close'],sims.ix[i,'X_volume'],sims.ix[i,'Y_close'],sims.ix[i,'Y_volume'])

# FF data (annualised)
FF_data = Quandl.get('KFRENCH/FACTORS_D',authtoken=auth,trim_start=trade_begin,trim_end=end_date,returns="pandas")*252/100
print(FF_data.head())

# ratios
Ratios = pd.DataFrame(columns=['Sharpe','Sortino'])
for i in range(0,len(sims)):
  df = dfs['df'+str(i)]
  Sharpe = (df.Return - FF_data.RF).mean()/np.sqrt(np.mean(np.power(df.Return - FF_data.RF,2)))
  Sortino = (df.Return - FF_data.RF).mean()/np.sqrt(np.mean(np.power(df.Return[df.Return < FF_data.RF] - FF_data.RF[df.Return < FF_data.RF],2)))
  Ratios.loc[i] = [Sharpe,Sortino]
Ratios = Ratios.set_index(sims.index)
print(Ratios)
  
# individual regressions
Indiv = pd.DataFrame(columns=['SMB','SMB R^2','SMB Sharpe','SMB Sortino','HML','HML R^2','HML Sharpe','HML Sortino','RF','RF R^2','RF Sharpe','RF Sortino','Mkt-RF','Mkt-RF R^2','Mkt-RF Sharpe','Mkt-RF Sortino'])
for i in range(0,len(sims)):
  df = dfs['df'+str(i)]
  SMB = OLS(df.Return,FF_data.SMB+0,missing='drop').fit()
  SMB_p = SMB.params['SMB']
  SMB_R2 = SMB.rsquared
  SMB_Sharpe = SMB.resid.mean()/np.sqrt(np.mean(np.power(SMB.resid,2)))
  SMB_Sortino = SMB.resid.mean()/np.sqrt(np.mean(np.power(SMB.resid[SMB.resid<0],2)))
  HML = OLS(df.Return,FF_data.HML+0,missing='drop').fit()
  HML_p = HML.params['HML']
  HML_R2 = HML.rsquared
  HML_Sharpe = HML.resid.mean()/np.sqrt(np.mean(np.power(HML.resid,2)))
  HML_Sortino = HML.resid.mean()/np.sqrt(np.mean(np.power(HML.resid[HML.resid<0],2)))
  RF = OLS(df.Return,FF_data.RF+0,missing='drop').fit()
  RF_p = RF.params['RF']
  RF_R2 = RF.rsquared
  RF_Sharpe = RF.resid.mean()/np.sqrt(np.mean(np.power(RF.resid,2)))
  RF_Sortino = RF.resid.mean()/np.sqrt(np.mean(np.power(RF.resid[RF.resid<0],2)))
  MktRF = OLS(df.Return,FF_data['Mkt-RF']+0,missing='drop').fit()
  MktRF_p = MktRF.params['Mkt-RF']
  MktRF_R2 = MktRF.rsquared
  MktRF_Sharpe = MktRF.resid.mean()/np.sqrt(np.mean(np.power(MktRF.resid,2)))
  MktRF_Sortino = MktRF.resid.mean()/np.sqrt(np.mean(np.power(MktRF.resid[MktRF.resid<0],2)))
  Indiv.loc[i] = [SMB_p,SMB_R2,SMB_Sharpe,SMB_Sortino,HML_p,HML_R2,HML_Sharpe,HML_Sortino,RF_p,RF_R2,RF_Sharpe,RF_Sortino,MktRF_p,MktRF_R2,MktRF_Sharpe,MktRF_Sortino]
Indiv = Indiv.set_index(sims.index)
print(Indiv)

# improvement individual regressions
Improv_Indiv = pd.DataFrame()
Improv_Indiv['SMB Sharpe'] = Indiv['SMB Sharpe'] - Ratios['Sharpe']
Improv_Indiv['SMB Sortino'] = Indiv['SMB Sortino'] - Ratios['Sortino']
Improv_Indiv['HML Sharpe'] = Indiv['HML Sharpe'] - Ratios['Sharpe']
Improv_Indiv['HML Sortino'] = Indiv['HML Sortino'] - Ratios['Sortino']
Improv_Indiv['RF Sharpe'] = Indiv['RF Sharpe'] - Ratios['Sharpe']
Improv_Indiv['RF Sortino'] = Indiv['RF Sortino'] - Ratios['Sortino']
Improv_Indiv['Mkt-RF Sharpe'] = Indiv['Mkt-RF Sharpe'] - Ratios['Sharpe']
Improv_Indiv['Mkt-RF Sortino'] = Indiv['Mkt-RF Sortino'] - Ratios['Sortino']
Improv_Indiv = Improv_Indiv.set_index(sims.index)
print(Improv_Indiv)

# multivariate regression
Multi = pd.DataFrame(columns=['ETF','SMB','HML','RF','Mkt-RF','R^2','Sharpe','Sortino'])
for i in range(0,len(sims)):
  df = dfs['df'+str(i)]
  Reg = OLS(df.Return,FF_data+0,missing='drop').fit()
  Reg_p = Reg.params
  Reg_R2 = Reg.rsquared
  Reg_Sharpe = Reg.resid.mean()/np.sqrt(np.mean(np.power(Reg.resid,2)))
  Reg_Sortino = Reg.resid.mean()/np.sqrt(np.mean(np.power(Reg.resid[Reg.resid<0],2)))
  Multi.loc[i] = ['df'+str(i),Reg_p['SMB'],Reg_p['HML'],Reg_p['RF'],Reg_p['Mkt-RF'],Reg_R2,Reg_Sharpe,Reg_Sortino]
Multi = Multi.set_index(sims.index)
print(Multi)  

# improvement multivariate regression
Improv_Multi = pd.DataFrame()
Improv_Multi['Sharpe'] = Multi['Sharpe'] - Ratios['Sharpe']
Improv_Multi['Sortino'] = Multi['Sortino'] - Ratios['Sortino']
Improv_Multi = Improv_Multi.set_index(sims.index)
print(Improv_Multi)

# plots
x_ax = np.array([0,1,2,3,4,5,6,7,8,9]) # string axis

plt.figure(1,figsize=(12,6))
plt.xticks(x_ax,sims.index)
plt.title('ETF Strategy Return Performance')
plt.ylabel('Sharpe/Sortino Ratios')
plt.plot(x_ax,Ratios.Sharpe,color='black')
plt.scatter(x_ax,Ratios.Sharpe,color='black')
plt.plot(x_ax,Ratios.Sortino,color='red')
plt.scatter(x_ax,Ratios.Sortino,color='red')
plt.legend(['Sharpe','Sortino'],loc='upper left')

fig = plt.figure(2,figsize=(20,8))
plt.subplots_adjust(hspace=0.5)
for i in range(0,len(sims)):
  ax = fig.add_subplot(2,5,i+1)
  sm.graphics.qqplot(dfs['df'+str(i)].Return,ax=ax)
  plt.axvline(x=0)
  plt.axhline(y=0)
  plt.title('ETF{}'.format(i))
  
plt.figure(3,figsize=(18,9))
plt.suptitle('Comparing Sharpe and Sortino Ratios of Returns and Individual Regressions',fontsize=20)
plt.subplot(211)
plt.xticks(x_ax,sims.index)
plt.plot(x_ax,Ratios['Sharpe'],color='black')
plt.plot(x_ax,Indiv['SMB Sharpe'])
plt.plot(x_ax,Indiv['HML Sharpe'])
plt.plot(x_ax,Indiv['Mkt-RF Sharpe'])
plt.title('Sharpe Ratio Comparison')
plt.ylabel('Sharpe Ratio')
plt.legend(['Returns','SMB','HML','Mkt-RF'],loc='center left',bbox_to_anchor=(1, 0.5))
plt.subplot(212)
plt.xticks(x_ax,sims.index)
plt.plot(x_ax,Ratios['Sortino'],color='black')
plt.plot(x_ax,Indiv['SMB Sortino'])
plt.plot(x_ax,Indiv['HML Sortino'])
plt.plot(x_ax,Indiv['Mkt-RF Sortino'])
plt.title('Sortino Ratio Comparison')
plt.ylabel('Sortino Ratio')
plt.legend(['Returns','SMB','HML','Mkt-RF'],loc='center left',bbox_to_anchor=(1, 0.5))

plt.figure(4,figsize=(18,9))
x_ax = np.array([0,1,2,3,4,5,6,7,8,9])
plt.suptitle('Comparing Sharpe and Sortino Ratios of Returns and Multivariate Regressions',fontsize=20)
plt.subplot(211)
plt.xticks(x_ax,sims.index)
plt.plot(x_ax,Ratios['Sharpe'],color='black')
plt.plot(x_ax,Multi['Sharpe'])
plt.title('Sharpe Ratio Comparison')
plt.ylabel('Sharpe Ratio')
plt.legend(['Returns','Multi'],loc='center left',bbox_to_anchor=(1, 0.5))
plt.subplot(212)
plt.xticks(x_ax,sims.index)
plt.plot(x_ax,Ratios['Sortino'],color='black')
plt.plot(x_ax,Multi['Sortino'])
plt.title('Sortino Ratio Comparison')
plt.ylabel('Sortino Ratio')
plt.legend(['Returns','Multi'],loc='center left',bbox_to_anchor=(1, 0.5))

#i = 8
#g=0.0019
#j=0.0007
#df = strat(sims.ix[i,'M'],g,j,sims.ix[i,'X_code'],sims.ix[i,'Y_code'],sims.ix[i,'X_close'],sims.ix[i,'X_volume'],sims.ix[i,'Y_close'],sims.ix[i,'Y_volume'])
## plot DeltaM with entry and exit points
#plt.figure(4,figsize=(16,8))
#plt.title('Difference in Returns Over M Days')
#plt.ylabel('Return Difference')
#df.DeltaM.plot(color='black')
#plt.axhline(y=g,color='green')
#plt.axhline(y=j,color='red')
#plt.axhline(y=-g,color='green')
#plt.axhline(y=-j,color='red')
#Entry_Pts = pd.DataFrame(df.Entry*df.DeltaM)
#Entry_Pts = Entry_Pts[Entry_Pts != 0]
#Exit_Pts = pd.DataFrame(df.Exit*df.DeltaM)
#Exit_Pts = Exit_Pts[Exit_Pts != 0]
#p1, = plt.plot(Entry_Pts,'g.')
#p2, = plt.plot(Exit_Pts,'r.')
#for i in range(0,len(df)):
#    if df.EOM[i] == 1:
#        plt.axvline(x=df.index[i],color='grey')
#plt.legend([p1,p2],['Entry Point','Exit Point'],
#           numpoints=1,loc='lower right')
#
## plot cumulative profit
#plt.figure(5,figsize=(16,8))
#plt.title('Cumulative Profit')
#plt.ylabel('Dollar Profit')
#df.Cum_Profit.plot(color='black')
#Entry_Pts = pd.DataFrame(df.Entry*df.Cum_Profit)
#Entry_Pts = Entry_Pts[Entry_Pts != 0]
#Exit_Pts = pd.DataFrame(df.Exit*df.Cum_Profit)
#Exit_Pts = Exit_Pts[Exit_Pts != 0]
#p1, = plt.plot(Entry_Pts,'g.')
#p2, = plt.plot(Exit_Pts,'r.')
#for i in range(0,len(df)):
#    if df.EOM[i] == 1:
#        plt.axvline(x=df.index[i],color='grey')
#plt.legend([p1,p2],['Entry Point','Exit Point'],
#           numpoints=1,loc='lower right')
#
#i=8
## check overall profit when widening the spread of g and j
#Perform_W = pd.DataFrame(columns = ['W','Cum_Profit'])
#for n in range(0,20):
#  n = n/10000
#  g = 0.002
#  j = 0.002-n
#  df = strat(sims.ix[i,'M'],g,j,sims.ix[i,'X_code'],sims.ix[i,'Y_code'],sims.ix[i,'X_close'],sims.ix[i,'X_volume'],sims.ix[i,'Y_close'],sims.ix[i,'Y_volume'])
#  Perform_W = Perform_W.append(pd.DataFrame([[g,j,g-j,df.Cum_Profit[-1]]],columns=['g','j','W','Cum_Profit']),
#      ignore_index=True)
#plt.figure(6)
#plt.plot(Perform_W.W,Perform_W.Cum_Profit,color='black') # window of 0.0011 looks good
#plt.title('Profit When Widening the Spread of g and j')
#plt.ylabel('Total Profit (dollars)')
#plt.xlabel('g-j')
#plt.grid()
