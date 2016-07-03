#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*#
# Michael Hyeong-Seok Beven              #
# University of Chicago                  #
# Financial Mathematics                  #
# Quantitative Strategies and Regression #
# Homework 6                             #
#~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*#

##########################
# ipython notebook setup #
##########################

from statsmodels.regression.linear_model import OLS
from statsmodels.robust.robust_linear_model import RLM # Huber, Tukey
import statsmodels.api as sm
import pandas as pd
import numpy as np
import Quandl
import keyring as kr # hidden password
key = kr.get_password('Quandl','mbeven')
import matplotlib.pyplot as plt
# %matplotlib inline
import os
os.chdir('/Users/michaelbeven/Documents/06_School/2016 Spring/FINM_2016_SPRING/FINM 33150/HW6')
import warnings
warnings.filterwarnings('ignore')
pd.set_option('display.notebook_repr_html', False)
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 100)
pd.set_option('display.width', 82)
pd.set_option('precision', 6)

##############
# parameters #
##############

start_date = '2016-01-01'
end_date = '2016-02-29'

########
# data #
########

#intial grab
codes = pd.read_csv('EOD-datasets-codes.csv',names=['code','desc']).code
count = 0 # count for non empty data sets
data = {}
codes_final = []
for i in range(0,len(codes)):
    data[codes[i]] = Quandl.get(codes[i],authtoken=key,trim_start=start_date,trim_end=end_date,returns="pandas").Adj_Close
    if len(data[codes[i]]) != 39:
        del data[codes[i]]
        continue
    data[codes[i]].to_csv('Data/' + codes[i].replace('/','') + '.csv')
    count = count + 1
    codes_final.append(codes[i])
    if count == 600:
        break
print('The number of non-empty data sets is {}'.format(count))
pd.DataFrame(codes_final).to_csv('Data/codes_final.csv')

#SPY data
P_SPY = pd.DataFrame(Quandl.get('EOD/SPY',authtoken=key,trim_start=start_date,trim_end=end_date,returns="pandas").Adj_Close)

#grab saved csv files
codes_final = pd.read_csv('Data/codes_final.csv').ix[:,1]

data = {}
for i in range(0,len(codes_final)):
    data[codes_final[i]] = pd.read_csv('Data/' + codes_final[i].replace('/','') + '.csv',names=['Adj_Close']).ix[:,0]
    data[codes_final[i]] = pd.DataFrame(data[codes_final[i]]).set_index(P_SPY.index)

############
# analysis #
############

# turn into returns
rets = {}
for key in data:
    P = data[key]
    R = np.log(P) - np.log(P.shift(1))
    rets[key] = R

R_SPY = np.log(P_SPY) - np.log(P_SPY.shift(1))

# run regressions
OLS_A = {}
OLS_B = {}
Huber_A = {}
Huber_B = {}
Tukey_A = {}
Tukey_B = {}
for key in rets:
    OLS_A[key] = OLS(rets[key][1:21],R_SPY[1:21],missing='drop').fit()
    OLS_B[key] = OLS(rets[key][1:21],sm.add_constant(R_SPY[1:21]),missing='drop').fit()
    Huber_A[key] = RLM(rets[key][1:21],R_SPY[1:21],missing='drop',M=sm.robust.norms.HuberT()).fit()
    Huber_B[key] = RLM(rets[key][1:21],sm.add_constant(R_SPY[1:21]),missing='drop',M=sm.robust.norms.HuberT()).fit()
    Tukey_A[key] = RLM(rets[key][1:21],R_SPY[1:21],missing='drop',M=sm.robust.norms.TukeyBiweight()).fit()
    Tukey_B[key] = RLM(rets[key][1:21],sm.add_constant(R_SPY[1:21]),missing='drop',M=sm.robust.norms.TukeyBiweight()).fit()

# residuals
resid_OLS_A = {}
resid_OLS_B = {}
resid_Huber_A = {}
resid_Huber_B = {}
resid_Tukey_A = {}
resid_Tukey_B = {}
for key in rets:
    resid_OLS_A[key] = rets[key][22:28] - R_SPY[22:28]*OLS_A[key].params[0]
    resid_OLS_B[key] = rets[key][22:28] - (R_SPY[22:28]*OLS_B[key].params[1] + OLS_B[key].params[0])
    resid_Huber_A[key] = rets[key][22:28] - R_SPY[22:28]*Huber_A[key].params[0]
    resid_Huber_B[key] = rets[key][22:28] - (R_SPY[22:28]*Huber_B[key].params[1] + Huber_B[key].params[0])
    resid_Tukey_A[key] = rets[key][22:28] - R_SPY[22:28]*Tukey_A[key].params[0]
    resid_Tukey_B[key] = rets[key][22:28] - (R_SPY[22:28]*Tukey_B[key].params[1] + Tukey_B[key].params[0])

# in-sample volatility
Vol_OLS_A = {}
Vol_OLS_B = {}
Vol_Huber_A = {}
Vol_Huber_B = {}
Vol_Tukey_A = {}
Vol_Tukey_B = {}
for key in rets:
    Vol_OLS_A[key] = OLS_A[key].resid.std()
    Vol_OLS_B[key] = OLS_B[key].resid.std()
    Vol_Huber_A[key] = Huber_A[key].resid.std()
    Vol_Huber_B[key] = Huber_B[key].resid.std()
    Vol_Tukey_A[key] = Tukey_A[key].resid.std()
    Vol_Tukey_B[key] = Tukey_B[key].resid.std()

#################
# performance 1 #
#################

resids_OLS_A = pd.DataFrame()
resids_OLS_B = pd.DataFrame()
resids_Huber_A = pd.DataFrame()
resids_Huber_B = pd.DataFrame()
resids_Tukey_A = pd.DataFrame()
resids_Tukey_B = pd.DataFrame()
for key in rets:
    resids_OLS_A = pd.concat((resids_OLS_A,pd.DataFrame(resid_OLS_A[key])),axis=0)
    resids_OLS_B = pd.concat((resids_OLS_B,pd.DataFrame(resid_OLS_B[key])),axis=0)
    resids_Huber_A = pd.concat((resids_Huber_A,pd.DataFrame(resid_Huber_A[key])),axis=0)
    resids_Huber_B = pd.concat((resids_Huber_B,pd.DataFrame(resid_Huber_B[key])),axis=0)
    resids_Tukey_A = pd.concat((resids_Tukey_A,pd.DataFrame(resid_Tukey_A[key])),axis=0)
    resids_Tukey_B = pd.concat((resids_Tukey_B,pd.DataFrame(resid_Tukey_B[key])),axis=0)

#resids plot
plt.figure(figsize=(14,14))
plt.suptitle('Residual Plots',fontsize=20)
x1 = plt.subplot(161)
plt.title('OLS_A')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_OLS_A.index,resids_OLS_A,'o')
x1 = plt.subplot(162)
plt.title('OLS_B')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_OLS_B.index,resids_OLS_B,'o')
plt.xlabel('')
x1 = plt.subplot(163)
plt.title('Huber_A')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_Huber_A.index,resids_Huber_A,'o')
plt.xlabel('')
x1 = plt.subplot(164)
plt.title('Huber_B')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_Huber_B.index,resids_Huber_B,'o')
plt.xlabel('')
x1 = plt.subplot(165)
plt.title('Tukey_A')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_Tukey_A.index,resids_Tukey_A,'o')
plt.xlabel('')
x1 = plt.subplot(166)
plt.title('Tukey_B')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_Tukey_B.index,resids_Tukey_B,'o')
plt.xlabel('')

#histograms
plt.figure(figsize=(14,14))
plt.suptitle('Histograms of Model Residuals (Bins=500)',fontsize=20)
x1 = plt.subplot(611)
x1.set_ylim([0,350])
plt.title('OLS_A')
hist1 = plt.hist(np.array(resids_OLS_A),500)
x1 = plt.subplot(612)
x1.set_ylim([0,350])
plt.title('OLS_B')
hist2 = plt.hist(np.array(resids_OLS_B),500)
x1 = plt.subplot(613)
x1.set_ylim([0,350])
plt.title('Huber_A')
hist3 = plt.hist(np.array(resids_Huber_A),500)
x1 = plt.subplot(614)
x1.set_ylim([0,350])
plt.title('Huber_B')
hist4 = plt.hist(np.array(resids_Huber_B),500)
x1 = plt.subplot(615)
x1.set_ylim([0,350])
plt.title('Tukey_A')
hist5 = plt.hist(np.array(resids_Tukey_A),500)
x1 = plt.subplot(616)
x1.set_ylim([0,350])
plt.title('Tukey_B')
hist6 = plt.hist(np.array(resids_Tukey_B),500)
plt.show()

#means by day
means_OLS_A = resids_OLS_A.groupby(resids_OLS_A.index).mean()
means_OLS_B = resids_OLS_B.groupby(resids_OLS_B.index).mean()
means_Huber_A = resids_Huber_A.groupby(resids_Huber_A.index).mean()
means_Huber_B = resids_Huber_B.groupby(resids_Huber_B.index).mean()
means_Tukey_A = resids_Tukey_A.groupby(resids_Tukey_A.index).mean()
means_Tukey_B = resids_Tukey_B.groupby(resids_Tukey_B.index).mean()
plt.figure(figsize=(10,10))
plt.plot(means_OLS_A.index,means_OLS_A,'o',clip_on=False)
plt.plot(means_OLS_B.index,means_OLS_B,'go',clip_on=False)
plt.plot(means_Huber_A.index,means_Huber_A,'ro',clip_on=False)
plt.plot(means_Huber_B.index,means_Huber_B,'mo',clip_on=False)
plt.plot(means_Tukey_A.index,means_Tukey_A,'o',color='black',clip_on=False)
plt.plot(means_Tukey_B.index,means_Tukey_B,'o',color='orange',clip_on=False)
plt.title('Means of Absolute Model Residuals')
plt.legend(['OLS_A','OLS_B','Huber_A','Huber_B','Tukey_A','Tukey_B'],loc='best',numpoints=1)
plt.show()

#stdev by day
std_OLS_A = resids_OLS_A.groupby(resids_OLS_A.index).std()
std_OLS_B = resids_OLS_B.groupby(resids_OLS_B.index).std()
std_Huber_A = resids_Huber_A.groupby(resids_Huber_A.index).std()
std_Huber_B = resids_Huber_B.groupby(resids_Huber_B.index).std()
std_Tukey_A = resids_Tukey_A.groupby(resids_Tukey_A.index).std()
std_Tukey_B = resids_Tukey_B.groupby(resids_Tukey_B.index).std()
plt.figure(figsize=(10,10))
plt.plot(means_OLS_A.index,std_OLS_A,'o',clip_on=False)
plt.plot(means_OLS_B.index,std_OLS_B,'go',clip_on=False)
plt.plot(means_Huber_A.index,std_Huber_A,'ro',clip_on=False)
plt.plot(means_Huber_B.index,std_Huber_B,'mo',clip_on=False)
plt.plot(means_Tukey_A.index,std_Tukey_A,'o',color='black',clip_on=False)
plt.plot(means_Tukey_B.index,std_Tukey_B,'o',color='orange',clip_on=False)
plt.title('Standard Deviations of Absolute Model Residuals')
plt.legend(['OLS_A','OLS_B','Huber_A','Huber_B','Tukey_A','Tukey_B'],loc='best',numpoints=1)
plt.show()

#overall t stat
t_OLS_A = resids_OLS_A.mean()[0]/resids_OLS_A.std()[0]
t_OLS_B = resids_OLS_B.mean()[0]/resids_OLS_B.std()[0]
t_Huber_A = resids_Huber_A.mean()[0]/resids_Huber_A.std()[0]
t_Huber_B = resids_Huber_B.mean()[0]/resids_Huber_B.std()[0]
t_Tukey_A = resids_Tukey_A.mean()[0]/resids_Tukey_A.std()[0]
t_Tukey_B = resids_Tukey_B.mean()[0]/resids_Tukey_B.std()[0]
print('t-stat of OLS_A: {}'.format(t_OLS_A))
print('t-stat of OLS_B: {}'.format(t_OLS_B))
print('t-stat of Huber_A: {}'.format(t_Huber_A))
print('t-stat of Huber_B: {}'.format(t_Huber_B))
print('t-stat of Tukey_A: {}'.format(t_Tukey_A))
print('t-stat of Tukey_B: {}'.format(t_Tukey_B))

#extreme data
abs(resids_OLS_A).max()
abs(resids_OLS_B).max()
abs(resids_Huber_A).max()
abs(resids_Huber_B).max()
abs(resids_Tukey_A).max()
abs(resids_Tukey_B).max()
print('Largest Absolute Residual of OLS_A: {}'.format((abs(resids_OLS_A).max()[0]-resids_OLS_A.mean()[0])/resids_OLS_A.std()[0]))
print('Largest Absolute Residual of OLS_B: {}'.format((abs(resids_OLS_B).max()[0]-resids_OLS_B.mean()[0])/resids_OLS_B.std()[0]))
print('Largest Absolute Residual of Huber_A: {}'.format((abs(resids_Huber_A).max()[0]-resids_Huber_A.mean()[0])/resids_Huber_A.std()[0]))
print('Largest Absolute Residual of Huber_B: {}'.format((abs(resids_Huber_B).max()[0]-resids_Huber_B.mean()[0])/resids_Huber_B.std()[0]))
print('Largest Absolute Residual of Tukey_A: {}'.format((abs(resids_Tukey_A).max()[0]-resids_Tukey_A.mean()[0])/resids_Tukey_A.std()[0]))
print('Largest Absolute Residual of Tukey_B: {}'.format((abs(resids_Tukey_B).max()[0]-resids_Tukey_B.mean()[0])/resids_Tukey_B.std()[0]))

#################
# performance 2 #
#################

resids_OLS_A = pd.DataFrame()
resids_OLS_B = pd.DataFrame()
resids_Huber_A = pd.DataFrame()
resids_Huber_B = pd.DataFrame()
resids_Tukey_A = pd.DataFrame()
resids_Tukey_B = pd.DataFrame()
for key in rets:
    resids_OLS_A = pd.concat((resids_OLS_A,pd.DataFrame(resid_OLS_A[key]/Vol_OLS_A[key])),axis=0)
    resids_OLS_B = pd.concat((resids_OLS_B,pd.DataFrame(resid_OLS_B[key]/Vol_OLS_B[key])),axis=0)
    resids_Huber_A = pd.concat((resids_Huber_A,pd.DataFrame(resid_Huber_A[key]/Vol_Huber_A[key])),axis=0)
    resids_Huber_B = pd.concat((resids_Huber_B,pd.DataFrame(resid_Huber_B[key]/Vol_Huber_B[key])),axis=0)
    resids_Tukey_A = pd.concat((resids_Tukey_A,pd.DataFrame(resid_Tukey_A[key]/Vol_Tukey_A[key])),axis=0)
    resids_Tukey_B = pd.concat((resids_Tukey_B,pd.DataFrame(resid_Tukey_B[key]/Vol_Tukey_B[key])),axis=0)

#resids plot
plt.figure(figsize=(14,14))
plt.suptitle('Residual Plots',fontsize=20)
x1 = plt.subplot(161)
plt.title('OLS_A')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_OLS_A.index,resids_OLS_A,'o')
x1 = plt.subplot(162)
plt.title('OLS_B')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_OLS_B.index,resids_OLS_B,'o')
plt.xlabel('')
x1 = plt.subplot(163)
plt.title('Huber_A')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_Huber_A.index,resids_Huber_A,'o')
plt.xlabel('')
x1 = plt.subplot(164)
plt.title('Huber_B')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_Huber_B.index,resids_Huber_B,'o')
plt.xlabel('')
x1 = plt.subplot(165)
plt.title('Tukey_A')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_Tukey_A.index,resids_Tukey_A,'o')
plt.xlabel('')
x1 = plt.subplot(166)
plt.title('Tukey_B')
x1.axes.get_xaxis().set_visible(False)
plt.plot(resids_Tukey_B.index,resids_Tukey_B,'o')
plt.xlabel('')

#histograms
plt.figure(figsize=(14,14))
plt.suptitle('Histograms of Model Residuals (Bins=500)',fontsize=20)
x1 = plt.subplot(611)
x1.set_ylim([0,250])
plt.title('OLS_A')
hist1 = plt.hist(np.array(resids_OLS_A),500)
x1 = plt.subplot(612)
x1.set_ylim([0,250])
plt.title('OLS_B')
hist2 = plt.hist(np.array(resids_OLS_B),500)
x1 = plt.subplot(613)
x1.set_ylim([0,250])
plt.title('Huber_A')
hist3 = plt.hist(np.array(resids_Huber_A),500)
x1 = plt.subplot(614)
x1.set_ylim([0,250])
plt.title('Huber_B')
hist4 = plt.hist(np.array(resids_Huber_B),500)
x1 = plt.subplot(615)
x1.set_ylim([0,250])
plt.title('Tukey_A')
hist5 = plt.hist(np.array(resids_Tukey_A),500)
x1 = plt.subplot(616)
x1.set_ylim([0,250])
plt.title('Tukey_B')
hist6 = plt.hist(np.array(resids_Tukey_B),500)
plt.show()

#means by day
means_OLS_A = resids_OLS_A.groupby(resids_OLS_A.index).mean()
means_OLS_B = resids_OLS_B.groupby(resids_OLS_B.index).mean()
means_Huber_A = resids_Huber_A.groupby(resids_Huber_A.index).mean()
means_Huber_B = resids_Huber_B.groupby(resids_Huber_B.index).mean()
means_Tukey_A = resids_Tukey_A.groupby(resids_Tukey_A.index).mean()
means_Tukey_B = resids_Tukey_B.groupby(resids_Tukey_B.index).mean()
plt.figure(figsize=(10,10))
plt.plot(means_OLS_A.index,means_OLS_A,'o',clip_on=False)
plt.plot(means_OLS_B.index,means_OLS_B,'go',clip_on=False)
plt.plot(means_Huber_A.index,means_Huber_A,'ro',clip_on=False)
plt.plot(means_Huber_B.index,means_Huber_B,'mo',clip_on=False)
plt.plot(means_Tukey_A.index,means_Tukey_A,'o',color='black',clip_on=False)
plt.plot(means_Tukey_B.index,means_Tukey_B,'o',color='orange',clip_on=False)
plt.title('Means of Absolute Model Residuals')
plt.legend(['OLS_A','OLS_B','Huber_A','Huber_B','Tukey_A','Tukey_B'],loc='best',numpoints=1)
plt.show()

#stdev by day
std_OLS_A = resids_OLS_A.groupby(resids_OLS_A.index).std()
std_OLS_B = resids_OLS_B.groupby(resids_OLS_B.index).std()
std_Huber_A = resids_Huber_A.groupby(resids_Huber_A.index).std()
std_Huber_B = resids_Huber_B.groupby(resids_Huber_B.index).std()
std_Tukey_A = resids_Tukey_A.groupby(resids_Tukey_A.index).std()
std_Tukey_B = resids_Tukey_B.groupby(resids_Tukey_B.index).std()
plt.figure(figsize=(10,10))
plt.plot(means_OLS_A.index,std_OLS_A,'o',clip_on=False)
plt.plot(means_OLS_B.index,std_OLS_B,'go',clip_on=False)
plt.plot(means_Huber_A.index,std_Huber_A,'ro',clip_on=False)
plt.plot(means_Huber_B.index,std_Huber_B,'mo',clip_on=False)
plt.plot(means_Tukey_A.index,std_Tukey_A,'o',color='black',clip_on=False)
plt.plot(means_Tukey_B.index,std_Tukey_B,'o',color='orange',clip_on=False)
plt.title('Standard Deviations of Absolute Model Residuals')
plt.legend(['OLS_A','OLS_B','Huber_A','Huber_B','Tukey_A','Tukey_B'],loc='best',numpoints=1)
plt.show()

#overall t stat
t_OLS_A = resids_OLS_A.mean()[0]/resids_OLS_A.std()[0]
t_OLS_B = resids_OLS_B.mean()[0]/resids_OLS_B.std()[0]
t_Huber_A = resids_Huber_A.mean()[0]/resids_Huber_A.std()[0]
t_Huber_B = resids_Huber_B.mean()[0]/resids_Huber_B.std()[0]
t_Tukey_A = resids_Tukey_A.mean()[0]/resids_Tukey_A.std()[0]
t_Tukey_B = resids_Tukey_B.mean()[0]/resids_Tukey_B.std()[0]
print('t-stat of OLS_A: {}'.format(t_OLS_A))
print('t-stat of OLS_B: {}'.format(t_OLS_B))
print('t-stat of Huber_A: {}'.format(t_Huber_A))
print('t-stat of Huber_B: {}'.format(t_Huber_B))
print('t-stat of Tukey_A: {}'.format(t_Tukey_A))
print('t-stat of Tukey_B: {}'.format(t_Tukey_B))

#extreme data
abs(resids_OLS_A).max()
abs(resids_OLS_B).max()
abs(resids_Huber_A).max()
abs(resids_Huber_B).max()
abs(resids_Tukey_A).max()
abs(resids_Tukey_B).max()
print('Largest Absolute Residual of OLS_A: {}'.format((abs(resids_OLS_A).max()[0]-resids_OLS_A.mean()[0])/resids_OLS_A.std()[0]))
print('Largest Absolute Residual of OLS_B: {}'.format((abs(resids_OLS_B).max()[0]-resids_OLS_B.mean()[0])/resids_OLS_B.std()[0]))
print('Largest Absolute Residual of Huber_A: {}'.format((abs(resids_Huber_A).max()[0]-resids_Huber_A.mean()[0])/resids_Huber_A.std()[0]))
print('Largest Absolute Residual of Huber_B: {}'.format((abs(resids_Huber_B).max()[0]-resids_Huber_B.mean()[0])/resids_Huber_B.std()[0]))
print('Largest Absolute Residual of Tukey_A: {}'.format((abs(resids_Tukey_A).max()[0]-resids_Tukey_A.mean()[0])/resids_Tukey_A.std()[0]))
print('Largest Absolute Residual of Tukey_B: {}'.format((abs(resids_Tukey_B).max()[0]-resids_Tukey_B.mean()[0])/resids_Tukey_B.std()[0]))
