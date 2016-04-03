# Michael Beven
# University of Chicago - Financial Mathematics
# FINM 33150 - Quantitative Strategies and Regression
# Homework 1 - Problem 4

# modules
import pandas as pd
from pandas.stats.api import ols
import matplotlib.pyplot as plt

# read in data
HEET = pd.read_csv('HEET.tab',header=0,sep='\t')
COO_0 = pd.read_csv('COO_0.tab',header=0,sep='\t')
COO_2700 = pd.read_csv('COO_2700.tab',header=0,sep='\t')
COO_2762 = pd.read_csv('COO_2762.tab',header=0,sep='\t')
COO_3026 = pd.read_csv('COO_3026.tab',header=0,sep='\t')

# interpret data with respective countries
COO_Belgium = COO_0
COO_Canada = COO_2700
COO_France = COO_2762
COO_Sweden = COO_3026

# fit linear regression with growth as dependent and timestamp as independent
regress = ols(y=HEET['Growth'], x=HEET['Timestamp'])
print(regress)

# interpolate results on country datasets
Growth_Belgium = regress.beta['intercept'] + regress.beta['x']*COO_Belgium['Timestamp']
Growth_Belgium.name = 'Growth'
COO_Belgium = pd.concat((COO_Belgium,Growth_Belgium),axis=1)
Growth_Canada = regress.beta['intercept'] + regress.beta['x']*COO_Canada['Timestamp']
Growth_Canada.name = 'Growth'
COO_Canada = pd.concat((COO_Canada,Growth_Canada),axis=1)
Growth_France = regress.beta['intercept'] + regress.beta['x']*COO_France['Timestamp']
Growth_France.name = 'Growth'
COO_France = pd.concat((COO_France,Growth_France),axis=1)
Growth_Sweden = regress.beta['intercept'] + regress.beta['x']*COO_Sweden['Timestamp']
Growth_Sweden.name = 'Growth'
COO_Sweden = pd.concat((COO_Sweden,Growth_Sweden),axis=1)

# view the interpolation data
print(COO_Belgium.head())
print(COO_Canada.head())
print(COO_France.head())
print(COO_Sweden.head())

# plot the points on one figure
plt.figure(1)
plt.scatter(COO_Belgium['DiscountRate'],COO_Belgium['Growth'],color='black')
plt.scatter(COO_Canada['DiscountRate'],COO_Canada['Growth'],color='blue')
plt.scatter(COO_France['DiscountRate'],COO_France['Growth'],color='red')
plt.scatter(COO_Sweden['DiscountRate'],COO_Sweden['Growth'],color='green')
