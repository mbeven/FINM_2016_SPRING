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
from statsmodels.regression.linear_model import OLS

# set global variables
auth = "v21snmSix9KyXBWc1RkF"
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
  df['Nt'] = pd.rolling_median(df.XDDV,15)# 15 day rolling median
  K = np.max(2*df.Nt) # capital - set K now that we have Nt
  df['XR'] = np.log(df.XP) - np.log(df.XP.shift(1)) #logrets
  df['YR'] = np.log(df.YP) - np.log(df.YP.shift(1))
  df['Delta'] = df.XR-df.YR # difference of X and Y
  df['DeltaM'] = pd.rolling_sum(df.Delta,M)#M day accumulated difference 
  df = df[df.index >= trade_begin] # drop unnecessary date range
  df['Signal'] = np.nan # add empty trade signal column
  df.Signal[df.DeltaM > g] = 1 # entering or maintaining trade
  df.Signal[df.DeltaM < -g] = -1 # entering or maintaining trade
  df.Signal[np.abs(df.DeltaM) < j] = 0 # exiting or out of trade
  df['EOM'] = np.nan # end of month
  df.EOM[(df.shift(1,freq='B').index.day <= 3) & (df.shift(1,freq='B').index.day-df.index.day < -1)] = 1 # day before 1st day
  df.Signal[(df.shift(1,freq='B').index.day <= 3) & (df.shift(1,freq='B').index.day-df.index.day < -1)] = 0
  for i in range(1,len(df)):
    if np.isnan(df.Signal[i]):# if between g and j
      df.Signal[i] = df.Signal[i-1] # fill in with current position
  df.Signal[((df.Signal == -1) & (df.DeltaM > j)) | (df.Signal == 1) & (df.DeltaM < j)] = 0
  df['Entry'] = 1*(((df.Signal == 1) | (df.Signal == -1)) & (df.shift(1).Signal == 0)) # entry point
  df['Exit'] = 1*((df.Signal == 0) & ((df.shift(1).Signal == 1) | (df.shift(1).Signal == -1))) # exit point
  df['Nx'] = np.round(df.Signal*df.Nt/100/df.XP,0) # size of X trade
  df['Ny'] = np.round(df.Signal*df.Nt/100/df.YP,0) # size of Y trade
  df['Profit'] = pd.DataFrame(df.Signal*(df.Nx.shift(1)*df.XP.shift(1)*df.XR)-df.Ny.shift(1)*df.YP.shift(1)*df.YR) # dollar profit(loss)
  df['Cum_Profit'] = np.cumsum(df.Profit) #cumulative profit
  df['K'] = np.round(K + df.Cum_Profit,0) # capital based on changes in profit  
  df['Return'] = 252*df.Profit/df.K.shift(1) # annualised returns  
  df = np.round(df,3) # round
  return df

# set up a dataframe of the simulations to run
sims = pd.DataFrame(columns=['M','g','j','X_code','Y_code','X_close','X_volume','Y_close','Y_volume'])
sims.loc[0] = [20,0.02,0.001,'EOD/RYU','EOD/XLU','EOD.RYU - Adj_Close','EOD.RYU - Adj_Volume','EOD.XLU - Adj_Close','EOD.XLU - Adj_Volume']
sims.loc[1] = [20,0.060,0.047,'EOD/IST','EOD/IYZ','EOD.IST - Adj_Close','EOD.IST - Adj_Volume','EOD.IYZ - Adj_Close','EOD.IYZ - Adj_Volume']
sims.loc[2] = [20,0.021,0.003,'EOD/RING','EOD/GDX','EOD.RING - Adj_Close','EOD.RING - Adj_Volume','EOD.GDX - Adj_Close','EOD.GDX - Adj_Volume']
sims.loc[3] = [20,0.045,0.003,'EOD/XSD','EOD/SMH','EOD.XSD - Adj_Close','EOD.XSD - Adj_Volume','EOD.SMH - Adj_Close','EOD.SMH - Adj_Volume']
sims.loc[4] = [20,0.0025,0.0015,'EOD/PBE','EOD/XBI','EOD.PBE - Adj_Close','EOD.PBE - Adj_Volume','EOD.XBI - Adj_Close','EOD.XBI - Adj_Volume']
sims.loc[5] = [20,0.02,0.014,'EOD/PXJ','EOD/OIH','EOD.PXJ - Adj_Close','EOD.PXJ - Adj_Volume','EOD.OIH - Adj_Close','EOD.OIH - Adj_Volume']
sims.loc[6] = [20,0.034,0.0015,'EOD/IEO','EOD/XOP','EOD.IEO - Adj_Close','EOD.IEO - Adj_Volume','EOD.XOP - Adj_Close','EOD.XOP - Adj_Volume']
sims.loc[7] = [20,0.055,0.013,'EOD/RTH','EOD/XRT','EOD.RTH - Adj_Close','EOD.RTH - Adj_Volume','EOD.XRT - Adj_Close','EOD.XRT - Adj_Volume']
sims.loc[8] = [20,0.0019,0.0007,'EOD/SIVR','EOD/SLV','EOD.SIVR - Adj_Close','EOD.SIVR - Adj_Volume','EOD.SLV - Adj_Close','EOD.SLV - Adj_Volume']
sims.loc[9] = [20,0.08,0.01,'EOD/HYLD','EOD/JNK','EOD.HYLD - Adj_Close','EOD.HYLD - Adj_Volume','EOD.JNK - Adj_Close','EOD.JNK - Adj_Volume']

# create all data frames
dfs = {}
for i in range(0,9):
  dfs['df'+str(i)] = strat(sims.ix[i,'M'],sims.ix[i,'g'],sims.ix[i,'j'],sims.ix[i,'X_code'],sims.ix[i,'Y_code'],sims.ix[i,'X_close'],sims.ix[i,'X_volume'],sims.ix[i,'Y_close'],sims.ix[i,'Y_volume'])

# FF data
FF_data = Quandl.get('KFRENCH/FACTORS_D',authtoken=auth,trim_start=trade_begin,trim_end=end_date,returns="pandas")

# analysis
Ratios = pd.DataFrame(columns=['ETF','Sharpe','Sortino'])  
for i in range(0,9):
  df = dfs['df'+str(i)]
  Sharpe = (np.mean(df.Return - FF_data['RF']/100))/np.sqrt(np.mean(np.power(df.Return - FF_data['RF']/100,2)))
  Sortino = (np.mean(df.Return - FF_data['RF']/100))/np.sqrt(np.mean(np.power(df.Return[df.Return > FF_data['RF']] - FF_data['RF'][dfs['df0'].Return > FF_data['RF']],2)))
  Ratios.loc[i] = ['df'+str(i),Sharpe,Sortino]
  
# individual regressions
Indiv = pd.DataFrame(columns=['ETF','SMB','SMB Sharpe','SMB Sortino','HML','HML Sharpe','HML Sortino','RF','RF Sharpe','RF Sortino','Mkt-RF','Mkt-RF Sharpe','Mkt-RF Sortino'])
for i in range(0,9):
  df = dfs['df'+str(i)]
  SMB = OLS(df.Return,FF_data.SMB,missing='drop').fit()
  SMB_p = SMB.params['SMB']
  SMB_Sharpe = np.mean(SMB.resid)/np.sqrt(np.mean(np.power(SMB.resid,2)))
  SMB_Sortino = np.mean(SMB.resid)/np.sqrt(np.mean(np.power(SMB.resid[SMB.resid>0],2)))
  HML = OLS(df.Return,FF_data.HML,missing='drop').fit()
  HML_p = HML.params['HML']
  HML_Sharpe = np.mean(HML.resid)/np.sqrt(np.mean(np.power(HML.resid,2)))
  HML_Sortino = np.mean(HML.resid)/np.sqrt(np.mean(np.power(HML.resid[HML.resid>0],2)))
  RF = OLS(df.Return,FF_data.RF,missing='drop').fit()
  RF_p = RF.params['RF']
  RF_Sharpe = np.mean(RF.resid)/np.sqrt(np.mean(np.power(RF.resid,2)))
  RF_Sortino = np.mean(RF.resid)/np.sqrt(np.mean(np.power(RF.resid[RF.resid>0],2)))
  MktRF = OLS(df.Return,FF_data['Mkt-RF'],missing='drop').fit()
  MktRF_p = MktRF.params['Mkt-RF']
  MktRF_Sharpe = np.mean(MktRF.resid)/np.sqrt(np.mean(np.power(MktRF.resid,2)))
  MktRF_Sortino = np.mean(MktRF.resid)/np.sqrt(np.mean(np.power(MktRF.resid[MktRF.resid>0],2)))
  Indiv.loc[i] = ['df'+str(i),SMB_p,SMB_Sharpe,SMB_Sortino,HML_p,HML_Sharpe,HML_Sortino,RF_p,RF_Sharpe,RF_Sortino,MktRF_p,MktRF_Sharpe,MktRF_Sortino]
  
# mutlvariate regressions
Multi = pd.DataFrame(columns=['ETF','SMB','HML','RF','Mkt-RF','Sharpe','Sortino'])
for i in range(0,9):
  df = dfs['df'+str(i)]
  Reg = OLS(df.Return,FF_data,missing='drop').fit()
  Reg_p = Reg.params
  Reg_Sharpe = np.mean(Reg.resid)/np.sqrt(np.mean(np.power(Reg.resid,2)))
  Reg_Sortino = np.mean(Reg.resid)/np.sqrt(np.mean(np.power(Reg.resid[Reg.resid>0],2)))
  Multi.loc[i] = ['df'+str(i),Reg_p['SMB'],Reg_p['HML'],Reg_p['RF'],Reg_p['Mkt-RF'],Reg_Sharpe,Reg_Sortino]
  
