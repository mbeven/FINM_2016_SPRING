#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*#
# Michael Hyeong-Seok Beven              #
# University of Chicago                  #
# Financial Mathematics                  #
# Quantitative Strategies and Regression #
# Final Project                          #
#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*#

################
# python setup #
################

import pandas as pd
import Quandl
import numpy as np
from numpy import sqrt, pi, log, exp, nan, isnan, cumsum, arange
from scipy.stats import norm
import datetime
import matplotlib.pyplot as plt
import keyring as kr # hidden password
key = kr.get_password('Quandl','mbeven')
import os
import warnings
warnings.filterwarnings('ignore')
pd.set_option('display.notebook_repr_html', False)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 30)
pd.set_option('display.width', 82)
pd.set_option('precision', 6)
project_path = '/Users/michaelbeven/Documents/06_School/2016 Spring/\
FINM_2016_SPRING/FINM 33150/Project'
images_directory = project_path+'/Pitchbook/Images/'

##############
# parameters #
##############

expiry = datetime.datetime(2016,6,17)#futures/option expiry
M = 10 #ewma history
l = 0.0016 #call wing threshold
k = 0.0006 #put wing threshold
B = 10 #wings of butterfly
K = 3*B #capital

########
# data #
########

os.chdir(project_path) # set to local machine
calls = pd.read_csv('Data/Calls/ESM6C_All.csv',index_col='Date').iloc[::-1]
calls.index = pd.to_datetime(calls.index)
puts = pd.read_csv('Data/Puts/ESM6P_All.csv',index_col='Date').iloc[::-1]
puts.index = pd.to_datetime(puts.index)
future = pd.read_csv('Data/ESM6_IDX.csv',index_col='Date').Close.iloc[::-1]
future.index = pd.to_datetime(future.index)
future = future[(future.index >= calls.index[0]) & (future.index <= \
calls.index[-1])] # match date range
rfr = Quandl.get('USTREASURY/BILLRATES',returns='pandas',\
trim_start='2015-06-19',trim_end='2016-05-21').ix[:,0]/100
rfr = rfr.reindex(calls.index,method='bfill') # two missing rfr points-smoothed

def clean_colnames(df):
    """
    Removes ' Index' suffix at the end and replaces ' ' with '_'
    """
    for col in df.columns:
        df.rename(columns={col:col.replace(' Index','')},inplace=True)
    for col in df.columns:
        df.rename(columns={col:col.replace(' ','_')},inplace=True)

clean_colnames(calls)
clean_colnames(puts)

print(pd.DataFrame([calls.columns,puts.columns]).transpose())

#empirical exploration
plt.figure()
plt.title('Call and Put Prices at 2015-06-25, S&P 500 E-mini June 2016')
plt.xlabel('Strike')
plt.ylabel('Price')
calls.ix['2015-06-25'].plot()
puts.ix['2015-06-25'].plot(ls='dashed')
plt.legend(['Calls','Puts'],loc='best')
plt.grid()
plt.savefig(images_directory+'option_prices.pdf')

#smooth prices
for i in range(0,len(calls)):
    calls.ix[i] = calls.ix[i].interpolate()
    puts.ix[i] = puts.ix[i].interpolate()
    
#empirical exploration
plt.figure()
plt.title('Call and Put Prices (Interpolated) at 2015-06-25, S&P 500 E-mini June 2016')
plt.xlabel('Strike')
plt.ylabel('Price')
calls.ix['2015-06-25'].plot()
puts.ix['2015-06-25'].plot(ls='dashed')
plt.legend(['Calls','Puts'],loc='best')
plt.grid()
plt.savefig(images_directory+'option_prices_interpolated.pdf')

############
# analysis #
############

def impvol(w, price, S, K, tau, r):
    """
    This function uses Newton's method to calculate implied vol.
    w: 1 for a call, -1 for a put
    price: price of the option
    S: price of the underlying
    K: strike
    tau: time to maturity in years (365 day convention)
    r: risk free rate (annualised 365 day convention)
    """
    v = sqrt(2*pi/tau)*price/S
    for i in range(1, 10):
        d1 = (log(S/K)+(r+0.5*pow(v,2))*tau)/(v*sqrt(tau))
        d2 = d1 - v*sqrt(tau)
        vega = S*norm.pdf(d1)*sqrt(tau)
        price0 = w*S*norm.cdf(w*d1) - w*K*exp(-r*tau)*norm.cdf(w*d2)
        v = v - (price0 - price)/vega
        if abs(price0 - price) < 1e-10 :
            break
    return v

def getdelta(cp, S, K, tau, r, v):
    """
    This function calculates delta of a call or put
    cp: 0 for call, 1 for put
    S: price of the underlying
    K: strike
    tau: time to maturity in years (365 day convention)
    r: risk free rate (annualised 365 day convention)
    v: volatility
    """
    d1 = (log(S/K)+(r+0.5*pow(v,2))*tau)/(v*sqrt(tau))
    return norm.cdf(d1) - cp

#implied vol tables
impvol_calls = calls*nan # empty table, same shape
for i in range (0,impvol_calls.shape[0]):
    for j in range (0,impvol_calls.shape[1]):
        impvol_calls.ix[i,j] = impvol(1,calls.ix[i,j],future.ix[i],\
        float(calls.columns[j][-4:]),\
        (expiry-calls.index[i].to_datetime()).days/365,rfr[i])

impvol_puts = puts*nan
for i in range (0,impvol_puts.shape[0]):
    for j in range (0,impvol_puts.shape[1]):
        impvol_puts.ix[i,j] = impvol(-1,puts.ix[i,j],future.ix[i],\
        float(puts.columns[j][-4:]),\
        (expiry-puts.index[i].to_datetime()).days/365,rfr[i])

#empirical exploration
plt.figure()
plt.title('Call and Put Implied Volatilities at 2015-06-25, S&P 500 E-mini June 2016')
plt.xlabel('Strike')
plt.ylabel('Volatility')
impvol_calls.ix['2015-06-25'].plot()
impvol_puts.ix['2015-06-25'].plot(ls='dashed')
plt.legend(['Calls','Puts'],loc='best')
plt.grid()
plt.savefig(images_directory+'option_implied_vols.pdf')

#calculate EWMA
ewma_calls = calls*nan #empty table
for column in impvol_calls:
    ewma_calls[column] = pd.ewma(impvol_calls[column],M)

ewma_puts = puts*nan
for column in impvol_puts:
    ewma_puts[column] = pd.ewma(impvol_puts[column],M)

#round underlying to strike increments
df = pd.concat((future,future.apply(lambda x: 5*round(float(x)/5))),axis=1)
df.columns = ['future','future_rounded']

#empirical exploration
plt.figure()
plt.title('S&P 500 E-mini Futures')
plt.xlabel('Time')
plt.ylabel('Index Level')
df.future.plot()
plt.grid()
plt.savefig(images_directory+'futures_ts.pdf')
print(df.future.mean())
print(df.future.std())

#compare means of EWMA to means of actual impvol each day
df['impvol_avg'] = nan #empty vector
df['ewma_avg'] = nan
#vol levels using 2 strikes on either side (call and put)
for i in range(0,df.shape[0]):
    df.impvol_avg[i] = (impvol_calls['ESM6C_'+str(df.future_rounded.ix[i])][i] +\
            impvol_puts['ESM6P_'+str(df.future_rounded.ix[i])][i] +\
            impvol_calls['ESM6C_'+str(df.future_rounded.ix[i]-10)][i] +\
            impvol_puts['ESM6P_'+str(df.future_rounded.ix[i]-10)][i] +\
            impvol_calls['ESM6C_'+str(df.future_rounded.ix[i]-5)][i] +\
            impvol_puts['ESM6P_'+str(df.future_rounded.ix[i]-5)][i] +\
            impvol_calls['ESM6C_'+str(df.future_rounded.ix[i]+5)][i] +\
            impvol_puts['ESM6P_'+str(df.future_rounded.ix[i]+5)][i] +\
            impvol_calls['ESM6C_'+str(df.future_rounded.ix[i]+10)][i] +\
            impvol_puts['ESM6P_'+str(df.future_rounded.ix[i]+10)][i])/10
    df.ewma_avg[i] = (ewma_calls['ESM6C_'+str(df.future_rounded.ix[i])][i] +\
            ewma_puts['ESM6P_'+str(df.future_rounded.ix[i])][i] +\
            ewma_calls['ESM6C_'+str(df.future_rounded.ix[i]-10)][i] +\
            ewma_puts['ESM6P_'+str(df.future_rounded.ix[i]-10)][i] +\
            ewma_calls['ESM6C_'+str(df.future_rounded.ix[i]-5)][i] +\
            ewma_puts['ESM6P_'+str(df.future_rounded.ix[i]-5)][i] +\
            ewma_calls['ESM6C_'+str(df.future_rounded.ix[i]+5)][i] +\
            ewma_puts['ESM6P_'+str(df.future_rounded.ix[i]+5)][i] +\
            ewma_calls['ESM6C_'+str(df.future_rounded.ix[i]+10)][i] +\
            ewma_puts['ESM6P_'+str(df.future_rounded.ix[i]+10)][i])/10

#empirical exploration
plt.figure()
plt.title('EWMA Predicted vs. Actual Implied Volatility')
plt.xlabel('Time')
plt.ylabel('Volatility')
df.impvol_avg.plot()
df.ewma_avg.plot(ls='dashed')
plt.grid()
plt.legend(['Actual Implied Volatility','EWMA Predicted Implied Volatility'],loc='best')
plt.savefig(images_directory+'ewma_actual_vol.pdf')

plt.figure()
plt.title('Histogram of EWMA Predicted Minus Actual Implied Volatility')
plt.xlabel('Difference')
plt.ylabel('Frequency')
(df.ewma_avg - df.impvol_avg).hist(bins=80)
plt.grid()
plt.savefig(images_directory+'vol_hist.pdf')
print((df.ewma_avg - df.impvol_avg).mean())
print((df.ewma_avg - df.impvol_avg).std())
# (optional) add vertical lines for standard dev

plt.figure()
plt.title('Quantiles of EWMA Predicted Minus Actual Implied Volatility')
plt.xlabel('Quantile')
plt.ylabel('Difference')
(df.ewma_avg - df.impvol_avg).quantile(arange(0,1.01,step=0.01)).plot()
plt.grid()
plt.savefig(images_directory+'vol_quantiles.pdf')

#build butterfly spread with delta hedge
df['signal'] = nan
df.signal[df.ewma_avg - df.impvol_avg > l] = 1 #buy butterfly
df.signal[df.ewma_avg - df.impvol_avg < -k] = -1 #sell butterfly
df['entry_strike'] = df.future_rounded*(1-isnan(df.signal))
df.signal[isnan(df.signal)] = 0
# track entry strike; find call and put prices accordingly
df['call_ATM'] = nan
df['put_ATM'] = nan
df['call_wing'] = nan
df['put_wing'] = nan
df['call_ATM_delta'] = nan
df['put_ATM_delta'] = nan
df['call_wing_delta'] = nan
df['put_wing_delta'] = nan
for i in range(1,len(df)):
    if df.signal[i] == 0:
        df.call_ATM[i] = 0
        df.put_ATM[i] = 0
        df.call_wing[i] = 0
        df.put_wing[i] = 0
        df.call_ATM_delta[i] = 0
        df.put_ATM_delta[i] = 0
        df.call_wing_delta[i] = 0
        df.put_wing_delta[i] = 0        
    else:
        df.call_ATM[i] = calls.ix[i]['ESM6C_'+str(df.entry_strike[i])]
        df.call_ATM_delta[i] = getdelta(0, df.future[i], df.entry_strike[i],\
        (expiry-df.index[i].to_datetime()).days/365,rfr[i], \
        impvol_calls.ix[i]['ESM6C_'+str(df.entry_strike[i])])
        df.put_ATM[i] = puts.ix[i]['ESM6P_'+str(df.entry_strike[i])]
        df.put_ATM_delta[i] = getdelta(1, df.future[i], df.entry_strike[i],\
        (expiry-df.index[i].to_datetime()).days/365,rfr[i], \
        impvol_puts.ix[i]['ESM6P_'+str(df.entry_strike[i])])
        df.call_wing[i] = calls.ix[i]['ESM6C_'+str(df.entry_strike[i]+B)]
        df.call_wing_delta[i] = getdelta(0, df.future[i], df.entry_strike[i]+B,\
        (expiry-df.index[i].to_datetime()).days/365,rfr[i],\
        impvol_calls.ix[i]['ESM6C_'+str(df.entry_strike[i]+10)])
        df.put_wing[i] = puts.ix[i]['ESM6P_'+str(df.entry_strike[i]-B)]
        df.put_wing_delta[i] = getdelta(1, df.future[i], df.entry_strike[i]+B,\
        (expiry-df.index[i].to_datetime()).days/365,rfr[i],\
        impvol_puts.ix[i]['ESM6P_'+str(df.entry_strike[i]-10)])
df['delta_hedge'] = df.call_ATM_delta + df.put_ATM_delta - (df.call_wing_delta\
 + df.put_wing_delta)
# track previous day's position value
df['call_ATM_old'] = nan
df['put_ATM_old'] = nan
df['call_wing_old'] = nan
df['put_wing_old'] = nan
for i in range(1,len(df)):
    if df.signal[i-1] == 0:
        df.call_ATM_old[i] = 0
        df.put_ATM_old[i] = 0
        df.call_wing_old[i] = 0
        df.put_wing_old[i] = 0
    else:
        df.call_ATM_old[i] = calls.ix[i]['ESM6C_'+str(df.entry_strike[i-1])]
        df.put_ATM_old[i] = puts.ix[i]['ESM6P_'+str(df.entry_strike[i-1])]
        df.call_wing_old[i] = calls.ix[i]['ESM6C_'+str(df.entry_strike[i-1]+B)]
        df.put_wing_old[i] = puts.ix[i]['ESM6P_'+str(df.entry_strike[i-1]-B)]
df = df[2:]
df['butterfly'] = df.signal*((df.call_wing + df.put_wing) - \
(df.call_ATM + df.put_ATM))
df['butterfly_old'] = df.shift(1).signal*((df.call_wing_old + \
df.put_wing_old) - (df.call_ATM_old + df.put_ATM_old))
df['profit'] = df.shift(1).butterfly - df.butterfly_old
df.profit[0] = df.signal[0]*((df.call_wing[0] + df.put_wing[0]) - \
(df.call_ATM[0] + df.put_ATM[0]))
df['cum_profit'] = cumsum(df.profit)

###########
# results #
###########

plt.figure()
plt.title('Cumulative Profit')
plt.xlabel('Time')
plt.ylabel('Daily Profit')
(df.cum_profit).plot()
plt.grid()
plt.savefig(images_directory+'Cum_Profit.pdf')

plt.figure()
plt.title('Cumulative Returns')
plt.xlabel('Time')
plt.ylabel('Percentage Return')
(df.cum_profit*100/K).plot()
plt.grid()
plt.savefig(images_directory+'cum_return.pdf')

#performance
df.cum_profit[-1]/K #total profit
df.cum_profit[-1]/K*(365/(df.index[-1]-df.index[0].to_datetime()).days)#annualised
(df.profit/K).std() * sqrt(365) # annualised standard dev of returns
(df.profit.mean() / df.profit.std()) # sharpe
df.profit.mean() / df.profit[df.profit < 0].std() # sortino
i = np.argmax(np.maximum.accumulate(df.cum_profit) - df.cum_profit)#drawdown end
j = np.argmax(df.cum_profit[:i]) #drawdown start
(df.cum_profit[i] - df.cum_profit[j])/K