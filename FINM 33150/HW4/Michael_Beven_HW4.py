#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*#
# Michael Beven                                        #
# University of Chicago - Financial Mathematics        #
# FINM 33150 - Quantitative Strategies and Regression  #
# Homework 4                                           #
#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*#

##########################
# ipython notebook setup #
##########################

import pandas as pd
import numpy as np
import Quandl
import keyring as kr # hidden password
key = kr.get_password('Quandl','mbeven')
import sqlite3 as sql
import time
import matplotlib.pyplot as plt
# %matplotlib inline
import warnings
db = '/Users/michaelbeven/Documents/06_School/2016 Spring/FINM_2016_SPRING/FINM 33150/HW4/Interbank_Rates.db'
warnings.filterwarnings('ignore')
pd.set_option('display.notebook_repr_html', False)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 20)
pd.set_option('display.width', 82)
pd.set_option('precision', 3)

##############
# parameters #
##############

notional = 10**7 # lending amount
K = 2*10**6 # capital
leverage= notional - K # borrowing amount
start_date = '2002-01-01'
end_date = time.strftime("%x") #today

##################
# rate functions #
##################

def compute_zcb_curve(spot_rates_curve):
    zcb_rates = spot_rates_curve.copy()
    for curve in spot_rates_curve.index:
        spot = spot_rates_curve[spot_rates_curve.index==curve]
        for tenor, spot_rate in spot.iteritems():
            if float(tenor)>0.001:
                times = np.arange(float(tenor)-0.25, 0, step=-0.25)[::-1]
                coupon_quarter_yr = float(0.25*spot_rate)
                z = np.interp(times, zcb_rates[spot_rates_curve.index==curve].columns.values.astype(float), zcb_rates[spot_rates_curve.index==curve].values[0,:]) # Linear interpolation
                preceding_coupons_val = (coupon_quarter_yr*np.exp(-z*times)).sum()
                zcb_rates.loc[spot_rates_curve.index==curve,tenor] = -np.log((1-preceding_coupons_val)/(1+coupon_quarter_yr))/float(tenor)
    return zcb_rates
    
def bond_price(zcb,c,T):
  bond_prices =  zcb.iloc[:,0]*0
  for curve in zcb.index:
    t = np.arange(T,0,step=-0.25)[::-1]
    r = np.interp(t,zcb[zcb.index==curve].columns.values.astype(float),zcb[zcb.index==curve].values[0,:]) # Linear interpolation
    p = np.exp(-T*r[-1]) + 0.25*c[curve]*np.exp(-r*t).sum()
    bond_prices[curve] = p
  return bond_prices

########
# data #
########

swap = {}
USDFX_codes = list(('CURRFX/USDGBP.1','CURRFX/USDEUR.1','CURRFX/USDAUD.1'))
USDFX = Quandl.get(USDFX_codes,authtoken=key,trim_start='2002-01-02',trim_end=end_date,returns="pandas",collapse='weekly').shift(1,freq='B')
USDFX.columns = ['USDGBP','USDEUR','USDAUD']
USDFX.USDAUD[USDFX.USDAUD<0.3]=1.28
LIBOR_codes = list(('FRED/USD3MTD156N','FRED/EUR3MTD156N','FRED/GBP3MTD156N','FRED/AUD3MTD156N'))
LIBOR = Quandl.get(LIBOR_codes,authtoken=key,trim_start=start_date,trim_end=end_date,returns="pandas").fillna(method='ffill')/100
LIBOR.columns = ['USD3M','EUR3M','GBP3M','AUD3M']
USDswap_codes = list(('FRED/DSWP1','FRED/DSWP2','FRED/DSWP5'))
USDswap = Quandl.get(USDswap_codes,authtoken=key,trim_start=start_date,trim_end=end_date,returns="pandas")/100
USDswap.columns = ['1','2','5']
cursor = sql.connect(db).cursor() # sql access
cursor.execute(("SELECT observation_date, rate FROM interbank_rates WHERE is_forward = 0 and tenor_years = '1.0' and currency = 'GBP' and observation_date >= '2002-01-01';"))
GBP1Yswap = pd.DataFrame(cursor.fetchall(),columns = ['date','1']).set_index('date').fillna(method='ffill')
GBP1Yswap = GBP1Yswap.set_index(pd.to_datetime(GBP1Yswap.index))
cursor.execute(("SELECT observation_date, rate FROM interbank_rates WHERE is_forward = 0 and tenor_years = '2.0' and currency = 'GBP' and observation_date >= '2002-01-01';"))
GBP2Yswap = pd.DataFrame(cursor.fetchall(),columns = ['date','2']).set_index('date').fillna(method='ffill')
GBP2Yswap = GBP2Yswap.set_index(pd.to_datetime(GBP2Yswap.index))
cursor.execute(("SELECT observation_date, rate FROM interbank_rates WHERE is_forward = 0 and tenor_years = '5.0' and currency = 'GBP' and observation_date >= '2002-01-01';"))
GBP5Yswap = pd.DataFrame(cursor.fetchall(),columns = ['date','5']).set_index('date').fillna(method='ffill')
GBP5Yswap = GBP5Yswap.set_index(pd.to_datetime(GBP5Yswap.index))
cursor.execute(("SELECT observation_date, rate FROM interbank_rates WHERE is_forward = 0 and tenor_years = '1.0' and currency = 'EUR' and observation_date >= '2002-01-01';"))
EUR1Yswap = pd.DataFrame(cursor.fetchall(),columns = ['date','1']).set_index('date').fillna(method='ffill')
EUR1Yswap = EUR1Yswap.set_index(pd.to_datetime(EUR1Yswap.index))
cursor.execute(("SELECT observation_date, rate FROM interbank_rates WHERE is_forward = 0 and tenor_years = '2.0' and currency = 'EUR' and observation_date >= '2002-01-01';"))
EUR2Yswap = pd.DataFrame(cursor.fetchall(),columns = ['date','2']).set_index('date').fillna(method='ffill')
EUR2Yswap = EUR2Yswap.set_index(pd.to_datetime(EUR2Yswap.index))
cursor.execute(("SELECT observation_date, rate FROM interbank_rates WHERE is_forward = 0 and tenor_years = '5.0' and currency = 'EUR' and observation_date >= '2002-01-01';"))
EUR5Yswap = pd.DataFrame(cursor.fetchall(),columns = ['date','5']).set_index('date').fillna(method='ffill')
EUR5Yswap = EUR5Yswap.set_index(pd.to_datetime(EUR5Yswap.index))
GBPswap = pd.concat((GBP1Yswap,GBP2Yswap,GBP5Yswap),axis=1)
EURswap = pd.concat((EUR1Yswap,EUR2Yswap,EUR5Yswap),axis=1)
swap['USD'] = USDswap.reindex(USDFX.index).fillna(method='bfill')
swap['GBP'] = GBPswap.reindex(USDFX.index).fillna(method='bfill')
swap['EUR'] = EURswap.reindex(USDFX.index).fillna(method='bfill')

####################
# lending currency #
####################

swap_zcb = {}
USDswap_zcb = compute_zcb_curve(USDswap).reindex(USDFX.index)
USDswap_zcb['BondLend'] = bond_price(USDswap_zcb,USDswap.reindex(USDFX.index)['5'],5)
USDswap_zcb['BondReturn'] = bond_price(USDswap_zcb.iloc[:,0:3],USDswap.reindex(USDFX.index)['5'],5-1/52)
USDswap_zcb['MTM'] = notional*(USDswap_zcb.BondReturn - USDswap_zcb.BondLend.shift(1))
swap_zcb['USD'] = USDswap_zcb.fillna(method='bfill')
GBPswap_zcb = compute_zcb_curve(GBPswap).reindex(USDFX.index)
GBPswap_zcb['BondLend'] = bond_price(GBPswap_zcb,GBPswap.reindex(USDFX.index)['5'],5)
GBPswap_zcb['BondReturn'] = bond_price(GBPswap_zcb.iloc[:,0:3],GBPswap.reindex(USDFX.index)['5'],5-1/52)
GBPswap_zcb['MTM'] = notional*(GBPswap_zcb.BondReturn*USDFX.USDGBP - GBPswap_zcb.BondLend.shift(1)*USDFX.shift(1).USDGBP)
swap_zcb['GBP'] = GBPswap_zcb.fillna(method='bfill')
EURswap_zcb = compute_zcb_curve(EURswap).reindex(USDFX.index)
EURswap_zcb['BondLend'] = bond_price(EURswap_zcb,EURswap.reindex(USDFX.index)['5'],5)
EURswap_zcb['BondReturn'] = bond_price(EURswap_zcb.iloc[:,0:3],EURswap.reindex(USDFX.index)['5'],5-1/52)
EURswap_zcb['MTM'] = notional*(EURswap_zcb.BondReturn*USDFX.USDEUR - EURswap_zcb.BondLend.shift(1)*USDFX.shift(1).USDEUR)
swap_zcb['EUR'] = EURswap_zcb.fillna(method='bfill')

######################
# borrowing currency #
######################

LIBOR['USDAccrued'] = leverage*1/52*(LIBOR.shift(1).USD3M+50/10000)
LIBOR['GBPAccrued'] = leverage*1/52*(LIBOR.shift(1).GBP3M+50/10000)*USDFX.USDGBP/USDFX.shift(1).USDGBP
LIBOR['EURAccrued'] = leverage*1/52*(LIBOR.shift(1).EUR3M+50/10000)*USDFX.USDEUR/USDFX.shift(1).USDEUR
LIBOR['AUDAccrued'] = leverage*1/52*(LIBOR.shift(1).AUD3M+50/10000)*USDFX.USDAUD/USDFX.shift(1).USDAUD

####################
# lending currency #
####################

LIBOR['USDAccrued_lend'] = notional*1/52*(LIBOR.shift(1).USD3M)
LIBOR['GBPAccrued_lend'] = notional*1/52*(LIBOR.shift(1).GBP3M)*USDFX.shift(1).USDGBP/USDFX.USDGBP
LIBOR['EURAccrued_lend'] = notional*1/52*(LIBOR.shift(1).EUR3M)*USDFX.shift(1).USDEUR/USDFX.USDEUR
LIBOR['AUDAccrued_lend'] = notional*1/52*(LIBOR.shift(1).AUD3M)*USDFX.shift(1).USDAUD/USDFX.USDAUD
LIBOR = LIBOR.reindex(USDFX.index).fillna(method='bfill')

#####################
# fixed-float swaps #
#####################

FF = pd.DataFrame(columns=['Fixed','Floating'])
FF.loc[0] = ['USD','GBP']
FF.loc[1] = ['USD','EUR']
FF.loc[2] = ['USD','AUD']
FF.loc[3] = ['GBP','USD']
FF.loc[4] = ['GBP','EUR']
FF.loc[5] = ['GBP','AUD']
FF.loc[6] = ['EUR','USD']
FF.loc[7] = ['EUR','GBP']
FF.loc[8] = ['EUR','AUD']

for pair in range(0,len(FF)):
  
  if FF.Floating[pair] == 'AUD':
    Signal = 1 + LIBOR.ix[:,0]*0
  else:  
    Signal = 1-1*(np.abs(swap[FF.Fixed[pair]]['5'] - swap[FF.Floating[pair]]['5']) <= 0.005)
    
  if FF.Fixed[pair] == 'USD':
    Fixed_CF = swap_zcb[FF.Fixed[pair]].MTM
  else:
    Fixed_CF = swap_zcb[FF.Fixed[pair]].MTM/USDFX['USD'+FF.Fixed[pair]]
  
  Floating_CF = LIBOR[FF.Floating[pair]+'Accrued']    
  df = pd.concat((Fixed_CF,Floating_CF,Signal),axis=1)
  df.columns = ['Fixed_CF','Floating_CF','Signal']
  df['Net_CF'] = df.Signal*(df.Fixed_CF - df.Floating_CF)
  df['Ret'] = df.Net_CF/K
  df['NegRet'] = df.Ret # needed for sortino ratio
  df.NegRet[df.Ret>=0] = np.nan
  df['CumRet'] = np.cumsum(df.Net_CF)/K 
  df['1YrRollingCumRet'] = pd.rolling_sum(df.Net_CF, 52).shift(1)/K
  df['1YrRollingSharpe'] = pd.rolling_mean(df.Ret,52).shift(1)/pd.rolling_std(df.Ret,52).shift(1)
  df['1YrRollingSortino'] = pd.rolling_mean(df.Ret,52).shift(1)/pd.rolling_std(df.NegRet,52,min_periods=1).shift(1)
  plt.figure(figsize=(14,14))
  plt.suptitle('Borrowing {}, Lending {} for Fixed-Float Swap Strategy'.format(FF.Floating[pair],FF.Fixed[pair]),fontsize=20)
  plt.subplot(511)
  plt.title('5Y Swap Rates')
  plt.plot(swap[FF.Fixed[pair]]['5'],label= FF.Fixed[pair])
  if FF.Floating[pair] != 'AUD':
    plt.plot(swap[FF.Floating[pair]]['5'],label= FF.Floating[pair])
  plt.legend([FF.Fixed[pair],FF.Floating[pair]],loc='best')
  plt.subplot(512)
  plt.title('Weekly Returns')
  plt.plot(df.Ret,color='red')
  plt.xlabel('')
  plt.subplot(513)
  plt.title('Cumulative Returns')
  plt.plot(df.CumRet,color='black')
  plt.plot(df['1YrRollingCumRet'],color='blue')
  plt.xlabel('')
  plt.legend(['Cumulative Weekly Return','Running Cumulative 1-Yr Weekly Return'],loc='best')
  plt.subplot(514)
  plt.title('Performance Ratios')
  plt.ylim(-20,20)
  plt.plot(df['1YrRollingSharpe'],color='green')
  plt.plot(df['1YrRollingSortino'],color='orange')
  plt.xlabel('')
  plt.legend(['Running 1-Year Sharpe Ratio','Running 1-Year Sortino Ratio'],loc='best')
  plt.subplot(515)
  plt.title('{}{}'.format(FF.Fixed[pair],FF.Floating[pair]))
  if FF.Fixed[pair] == 'USD':
    plt.plot(USDFX[str('USD'+FF.Floating[pair])],color='magenta')
  elif FF.Floating[pair] == 'USD':
    plt.plot(1/USDFX[str('USD'+FF.Fixed[pair])],color='magenta')
  else:
    plt.plot(USDFX[str('USD'+FF.Floating[pair])]/USDFX[str('USD'+FF.Fixed[pair])],color='magenta')
  plt.show()

###############
# basis swaps #
###############

B = pd.DataFrame(columns=['Fund','Borrow'])
B.loc[0] = ['USD','GBP']
B.loc[1] = ['USD','EUR']
B.loc[2] = ['USD','AUD']
B.loc[3] = ['GBP','USD']
B.loc[4] = ['GBP','EUR']
B.loc[5] = ['GBP','AUD']
B.loc[6] = ['EUR','USD']
B.loc[7] = ['EUR','GBP']
B.loc[8] = ['EUR','AUD']
B.loc[9] = ['AUD','USD']
B.loc[10] = ['AUD','GBP']
B.loc[11] = ['AUD','EUR']

for pair in range(0,len(B)):
  Fund_CF = LIBOR[B.Fund[pair]+'Accrued_lend']
  Borrow_CF = LIBOR[B.Borrow[pair]+'Accrued']

  df = pd.concat((Fund_CF,Borrow_CF),axis=1)
  df.columns = ['Fund_CF','Borrow_CF']
  df['Net_CF'] = df.Fund_CF - df.Borrow_CF
  df['Ret'] = df.Net_CF/K
  df['NegRet'] = df.Ret # needed for sortino ratio
  df.NegRet[df.Ret>=0] = np.nan
  df['CumRet'] = np.cumsum(df.Net_CF)/K 
  df['1YrRollingCumRet'] = pd.rolling_sum(df.Net_CF, 52).shift(1)/K
  df['1YrRollingSharpe'] = pd.rolling_mean(df.Ret,52).shift(1)/pd.rolling_std(df.Ret,52).shift(1)
  df['1YrRollingSortino'] = pd.rolling_mean(df.Ret,52).shift(1)/pd.rolling_std(df.NegRet,52,min_periods=1).shift(1)
  plt.figure(figsize=(14,14))
  plt.suptitle('Borrowing {}, Lending {} for Basis Swap Strategy'.format(B.Borrow[pair],B.Fund[pair]),fontsize=20)
  plt.subplot(511)
  plt.title('3M LIBOR Rates')
  plt.plot(LIBOR[B.Fund[pair]+'3M'],label= B.Fund[pair])
  plt.plot(LIBOR[B.Borrow[pair]+'3M']+0.005,label= B.Borrow[pair]+'+50bps')
  plt.legend([B.Fund[pair],B.Borrow[pair]+'+50bps'],loc='best')
  plt.subplot(512)
  plt.title('Weekly Returns')
  plt.plot(df.Ret,color='red')
  plt.xlabel('')
  plt.subplot(513)
  plt.title('Cumulative Returns')
  plt.plot(df.CumRet,color='black')
  plt.plot(df['1YrRollingCumRet'],color='blue')
  plt.xlabel('')
  plt.legend(['Cumulative Weekly Return','Running Cumulative 1-Yr Weekly Return'],loc='best')
  plt.subplot(514)
  plt.title('Performance Ratios')
  plt.ylim(-20,20)
  plt.plot(df['1YrRollingSharpe'],color='green')
  plt.plot(df['1YrRollingSortino'],color='orange')
  plt.xlabel('')
  plt.legend(['Running 1-Year Sharpe Ratio','Running 1-Year Sortino Ratio'],loc='best')
  plt.subplot(515)
  plt.title('{}{}'.format(B.Fund[pair],B.Borrow[pair]))
  if B.Fund[pair] == 'USD':
    plt.plot(USDFX[str('USD'+B.Borrow[pair])],color='magenta')
  elif B.Borrow[pair] == 'USD':
    plt.plot(1/USDFX[str('USD'+B.Fund[pair])],color='magenta')
  else:
    plt.plot(USDFX[str('USD'+B.Borrow[pair])]/USDFX[str('USD'+B.Fund[pair])],color='magenta')
  plt.show()
  
  
#────────────────────██████────────── 
#──────────────────██▓▓▓▓▓▓██──────── 
#────────────────██▓▓▓▓▒▒▒▒██──────── 
#────────────────██▓▓▒▒▒▒▒▒██──────── 
#──────────────██▓▓▓▓▒▒▒▒██────────── 
#──────────────██▓▓▒▒▒▒▒▒██────────── 
#────────────██▓▓▓▓▒▒▒▒▒▒██────────── 
#────────────████▒▒████▒▒██────────── 
#────────────██▓▓▒▒▒▒▒▒▒▒██────────── 
#──────────██────▒▒────▒▒██────────── 
#──────────████──▒▒██──▒▒██────────── 
#──────────██────▒▒────▒▒██────────── 
#──────────██▒▒▒▒▒▒▒▒▒▒▒▒██────────── 
#──────────████████████▒▒▒▒██──────── 
#────────██▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒██────── 
#──────██▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▒▒██──── 
#────██▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▒▒▒▒██── 
#──██▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▒▒▒▒██ 
#██▓▓▒▒▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▒▒▒▒██ 
#██▓▓▒▒▓▓▒▒▒▒▒▒▓▓▓▓▒▒▒▒▒▒▒▒▒▒▓▓▓▓▒▒██ 
#██▓▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▓▓▓▓██ 
#──████▐▌▓▓▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐▌▐▌████── 
#────██▐▌▐▌▌▌▌▌▌▌▌▌▐▌▐▌▐▌▐▌▌▌▐▌██──── 
#────██▌▌▐▌▐▌▌▌▐▌▌▌▌▌▐▌▌▌▌▌▌▌▌▌██──── 
#──────██▌▌▐▌▐▌▐▌▐▌▐▌▐▌▐▌▌▌▌▌██────── 
#──────██▐▌▐▌▐▌████████▐▌▌▌▌▌██────── 
#────────██▒▒██────────██▒▒██──────── 
#────────██████────────██████────────
