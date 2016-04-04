# Michael Beven
# University of Chicago - Financial Mathematics
# FINM 33150 - Quantitative Strategies and Regression
# Homework 1 - Problem 4

# modules
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

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

# linear interpolation of HEET data of growth using timestamp
interp = interp1d(HEET['Timestamp'],HEET['Growth'])

# interpolate results on country datasets
Growth_Belgium = pd.DataFrame(interp(COO_Belgium.iloc[:,0]))
Growth_Belgium.columns = ['Growth']
COO_Belgium = pd.concat((COO_Belgium,Growth_Belgium),axis=1)
Growth_Canada = pd.DataFrame(interp(COO_Canada.iloc[:,1]))
Growth_Canada.columns = ['Growth']
COO_Canada = pd.concat((COO_Canada,Growth_Canada),axis=1)
Growth_France = pd.DataFrame(interp(COO_France.iloc[:,1]))
Growth_France.columns = ['Growth']
COO_France = pd.concat((COO_France,Growth_France),axis=1)
Growth_Sweden = pd.DataFrame(interp(COO_Sweden.iloc[:,1]))
Growth_Sweden.columns = ['Growth']
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
plt.ylabel('Growth')
plt.xlabel('DiscountRate')
plt.title('Effect of Discount Rate on Growth')
plt.legend(['Belgium','Canada','France','Sweden'],loc='upper left')
plt.savefig('GrowthPlot',format='pdf')

# extra credit

# interpret data with respective countries
COO_Belgium_ec = COO_0
COO_Canada_ec = COO_2700
COO_France_ec = COO_2762
COO_Sweden_ec = COO_3026

# linear interpolation of HEET data of growth using GDP
interp = interp1d(HEET['GDP'],HEET['Growth'],bounds_error=False)

# interpolate results on country datasets
Growth_Canada = pd.DataFrame(interp(COO_Canada_ec.iloc[:,0]))
Growth_Canada.columns = ['Growth']
COO_Canada_ec = pd.concat((COO_Canada_ec,Growth_Canada),axis=1)
Growth_France = pd.DataFrame(interp(COO_France_ec.iloc[:,0]))
Growth_France.columns = ['Growth']
COO_France_ec = pd.concat((COO_France_ec,Growth_France),axis=1)
Growth_Sweden = pd.DataFrame(interp(COO_Sweden_ec.iloc[:,0]))
Growth_Sweden.columns = ['Growth']
COO_Sweden_ec = pd.concat((COO_Sweden_ec,Growth_Sweden),axis=1)

# view the interpolation data
print(COO_Canada_ec.head())
print(COO_France_ec.head())
print(COO_Sweden_ec.head())

# plot the points on one figure
plt.figure(2)
plt.scatter(COO_Canada_ec['DiscountRate'],COO_Canada_ec['Growth'],color='blue')
plt.scatter(COO_France_ec['DiscountRate'],COO_France_ec['Growth'],color='red')
plt.scatter(COO_Sweden_ec['DiscountRate'],COO_Sweden_ec['Growth'],color='green')
plt.ylabel('Growth')
plt.xlabel('DiscountRate')
plt.title('Effect of Discount Rate on Growth')
plt.legend(['Canada','France','Sweden'],loc='upper left')
plt.savefig('GrowthPlot_GDP',format='pdf')

# put both plots into one
fig = plt.figure(3)
fig.suptitle('Effect of Discount Rate on Growth')
plt.subplot(121)
plt.scatter(COO_Belgium['DiscountRate'],COO_Belgium['Growth'],color='black')
plt.scatter(COO_Canada['DiscountRate'],COO_Canada['Growth'],color='blue')
plt.scatter(COO_France['DiscountRate'],COO_France['Growth'],color='red')
plt.scatter(COO_Sweden['DiscountRate'],COO_Sweden['Growth'],color='green')
plt.ylabel('Growth')
plt.xlabel('DiscountRate')
plt.legend(['Belgium','Canada','France','Sweden'],loc='upper left')
plt.subplot(122)
plt.scatter(COO_Canada_ec['DiscountRate'],COO_Canada_ec['Growth'],color='blue')
plt.scatter(COO_France_ec['DiscountRate'],COO_France_ec['Growth'],color='red')
plt.scatter(COO_Sweden_ec['DiscountRate'],COO_Sweden_ec['Growth'],color='green')
plt.ylabel('Growth')
plt.xlabel('DiscountRate')
plt.legend(['Canada','France','Sweden'],loc='upper left')
plt.savefig('GrowthPlot_Both',format='pdf')
