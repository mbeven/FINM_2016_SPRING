#===========================================#
# Michael Hyeong-Seok Beven                 #
# University of Chicago                     #
# Financial Mathematics                     #
# Homework Assignment on Statistical Models #
# 20160510                                  #
#===========================================#

#########
# setup #
#########

rm(list=ls())
library(TTR) # rolling calculations
library(PerformanceAnalytics) # time series data

####################
# prepare the data #
####################
setwd('/Users/michaelbeven/Documents/06_School/2016 Spring/FINM_2016_SPRING/FINM 33601/Week 4')
df <- as.data.frame(read.csv('assignments-Fixed Income Derivatives-Assignment Lecture 4- Statistical Model-StatisticalModelData2014.csv'))
rownames(df) <- as.Date(df$Date,format='%m/%d/%Y')
df <- df[colnames(df)[2:8]]
maturities <- c(0.25,0.5,2,3,5,10,30) #maturities of instruments
print(head(df))

#########################################
# estimate the 3-factor model using PCA #
#########################################

# define factor and factor loadings
df.cov <- cov(df) # covariance matrix
eigenvectors <- eigen(df.cov)$vectors
eigenvalues <- eigen(df.cov)$values
PC <- as.matrix(df) %*% eigenvectors # principal components
print(df.cov)
print(eigenvectors)
print(eigenvalues)
print(head(PC))

# calculate relative importance of factors
print(round(eigenvalues/sum(eigenvalues)*100,2))
plot(round(eigenvalues/sum(eigenvalues)*100,2),pch=20,main='Eigenvalues',ylab='Score',xlab='Factor')
abline(a=0,b=0,lty=2)
print(round(cumsum(eigenvalues)/sum(eigenvalues)*100,2))

# plot and interpret the shapes of factor loadings
plot(maturities,eigenvectors[,1],type='l',ylim=c(-1,1),main='Factor Loadings',
     xlab='Maturities',ylab='Loadings')
lines(maturities,eigenvectors[,2],col='red')
lines(maturities,eigenvectors[,3],col='blue')
legend('top',c("1","2",'3'),lty=c(1,1),col=c('black','red','blue'),cex=1)

#############################################################################
# calculate historical volatilities and correlation coefficients of factors #
#############################################################################

# use the whole period of history to calculate var and cor
delta.fi <- diff(PC[,1:3])
print(diag(var(delta.fi)))
print(cor(delta.fi))

# calculate the same variables using a rolling window (approx 1 month)
plot.dates <- as.Date(rownames(runSD(delta.fi[,1]))) 
plot(plot.dates,runSD(delta.fi[,1],n=28),type='l',
     main='Volatilities of Factors 1 to 3, 
     28 Day Window',ylab='Standard Deviation of Daily Changes',xlab='Date')
lines(plot.dates,runSD(delta.fi[,2],n=28),col='red')
lines(plot.dates,runSD(delta.fi[,3],n=28),col='blue')

####################################################################
# find historical estimates of volatilities of the first 3 factors #
# corresponding to the last month of the observed period           #
####################################################################

PC.sub <- subset(PC[,1:3],rownames(PC)>='2014-06-01')
print(diag(var(PC.sub)))

###########################################################################
# calculate time series of each of the seven rates predicted by the model #
###########################################################################

pred3M <- PC[,1:3] %*% eigenvectors[1,][1:3]
plot.dates <- as.Date(rownames(pred3M)) 
plot(plot.dates,pred3M,type='l',main='3 Month Rate',xlab='Date')
lines(plot.dates,df[,1],col='red')

pred6M <- PC[,1:3] %*% eigenvectors[2,][1:3]
plot.dates <- as.Date(rownames(pred6M)) 
plot(plot.dates,pred6M,type='l',main='6 Month Rate',xlab='Date')
lines(plot.dates,df[,2],col='red')

pred2Y <- PC[,1:3] %*% eigenvectors[3,][1:3]
plot.dates <- as.Date(rownames(pred2Y)) 
plot(plot.dates,pred2Y,type='l',main='2 Year Rate',xlab='Date')
lines(plot.dates,df[,3],col='red')

pred3Y <- PC[,1:3] %*% eigenvectors[4,][1:3]
plot.dates <- as.Date(rownames(pred3Y)) 
plot(plot.dates,pred3Y,type='l',main='3 Year Rate',xlab='Date')
lines(plot.dates,df[,4],col='red')

pred5Y <- PC[,1:3] %*% eigenvectors[5,][1:3]
plot.dates <- as.Date(rownames(pred5Y)) 
plot(plot.dates,pred5Y,type='l',main='5 Year Rate',xlab='Date')
lines(plot.dates,df[,5],col='red')

pred10Y <- PC[,1:3] %*% eigenvectors[6,][1:3]
plot.dates <- as.Date(rownames(pred10Y)) 
plot(plot.dates,pred10Y,type='l',main='10 Year Rate',xlab='Date')
lines(plot.dates,df[,6],col='red')

pred30Y <- PC[,1:3] %*% eigenvectors[7,][1:3]
plot.dates <- as.Date(rownames(pred30Y)) 
plot(plot.dates,pred30Y,type='l',main='10 Year Rate',xlab='Date')
lines(plot.dates,df[,7],col='red')

#################################################################
# fit parametric forms from slide 32 to each of the first three #
# vectors of factor loadings                                    #
#################################################################

Loading.1 <- matrix(c(0.320,0.006,36.550,0.070,0.285,-0.292),nrow=3,ncol=2)
rownames(Loading.1) <- c(1,2,3)
colnames(Loading.1) <- c('a','b')
L.bound.1 <- c(0,0,0,-Inf,-Inf,-Inf)

Loading.2 <- matrix(c(0.650,0.004,-1.130,0.539),nrow=2,ncol=2)
rownames(Loading.2) <- c(1,2)
colnames(Loading.2) <- c('a','b')
L.bound.2 <- c(0,0,-Inf,-Inf)

Loading.3 <- matrix(c(4.200e-01,5e-08,5e-01,2.876,-1.92,0.62,-0.41,3.035),nrow=4,ncol=2)
rownames(Loading.3) <- c(1,2,3,4)
colnames(Loading.3) <- c('a','b')
L.bound.3 <- c(0,0,0,0,-Inf,-Inf,-Inf,-Inf)

fn <- function(mat) {
  mat <- matrix(mat,ncol=2)
  return(abs(pca.loading - sum(mat[,2] * (1-exp(-mat[,1]*tau))/(mat[,1]*tau))))}

# Loading 1
tau <- 0.25
pca.loading <- eigenvectors[1,1]
print(round(optim(Loading.1,fn,method='L-BFGS-B')$par,4))
tau <- 0.5
pca.loading <- eigenvectors[2,1]
print(round(optim(Loading.1,fn,method='L-BFGS-B',lower=L.bound.1)$par,4))
tau <- 2
pca.loading <- eigenvectors[3,1]
print(round(optim(Loading.1,fn,method='L-BFGS-B',lower=L.bound.1)$par,4))
tau <- 3
pca.loading <- eigenvectors[4,1]
print(round(optim(Loading.1,fn,method='L-BFGS-B',lower=L.bound.1)$par,4))
tau <- 5
pca.loading <- eigenvectors[5,1]
print(round(optim(Loading.1,fn,method='L-BFGS-B',lower=L.bound.1)$par,4))
tau <- 10
pca.loading <- eigenvectors[6,1]
print(round(optim(Loading.1,fn,method='L-BFGS-B',lower=L.bound.1)$par,4))
tau <- 30
pca.loading <- eigenvectors[7,1]
print(round(optim(Loading.1,fn,method='L-BFGS-B',lower=L.bound.1)$par,4))

# Loading 2 
tau <- 0.25
pca.loading <- eigenvectors[1,2]
print(round(optim(Loading.2,fn,method='L-BFGS-B',lower=L.bound.2)$par,4))
tau <- 0.5 
pca.loading <- eigenvectors[2,2]
print(round(optim(Loading.2,fn,method='L-BFGS-B',lower=c(0,0,0,0))$par,4))
tau <- 2 
pca.loading <- eigenvectors[3,2]
print(round(optim(Loading.2,fn,method='L-BFGS-B',lower=c(0,0,0,0))$par,4))
tau <- 3
pca.loading <- eigenvectors[4,2]
print(round(optim(Loading.2,fn,method='L-BFGS-B',lower=L.bound.2)$par,4))
tau <- 5 
pca.loading <- eigenvectors[5,2]
print(round(optim(Loading.2,fn,method='L-BFGS-B',lower=L.bound.2)$par,4))
tau <- 10 
pca.loading <- eigenvectors[6,2]
print(round(optim(Loading.2,fn,method='L-BFGS-B')$par,4))
tau <- 30 
pca.loading <- eigenvectors[7,2]
print(round(optim(Loading.2,fn,method='L-BFGS-B')$par,4))

# Loading 3 
tau <- 0.25
pca.loading <- eigenvectors[1,3]
print(round(optim(Loading.3,fn,method='L-BFGS-B')$par,4))
tau <- 0.5 
pca.loading <- eigenvectors[2,3]
print(round(optim(Loading.3,fn,method='L-BFGS-B')$par,4))
tau <- 2
pca.loading <- eigenvectors[3,3]
print(round(optim(Loading.3,fn,method='L-BFGS-B')$par,4))
tau <- 3
pca.loading <- eigenvectors[4,3]
print(round(optim(Loading.3,fn,method='L-BFGS-B')$par,4))
tau <- 5 
pca.loading <- eigenvectors[5,3]
print(round(optim(Loading.3,fn,method='L-BFGS-B')$par,4))
tau <- 10 
pca.loading <- eigenvectors[6,3]
print(round(optim(Loading.3,fn,method='L-BFGS-B')$par,4))
tau <- 30 
pca.loading <- eigenvectors[7,3]
print(round(optim(Loading.3,fn)$par,4))

#############################################################################
# calculate time series of instataneous forward rates with maturity 5 years #
# and discount bonds with maturity 4.5 year for whole period of observation #
#############################################################################

forward <- 5*(PC[,1:3] %*% eigenvectors[5,][1:3]) + colMeans(df)[5]*5
loadings <- eigenvectors[5,][1:3] - (eigenvectors[5,][1:3] - eigenvectors[4,][1:3])/4
disc.mean <- colMeans(df)[5] - (colMeans(df)[5] - colMeans(df)[4])/2
disc.rates <- exp(-(((4.5*disc.mean) + (PC[,1:3] %*% loadings * 4.5)))/100)

hist(diff(forward),breaks=100,main='Histogram of 1 Day Increments of the Instantaneous Forward',
     xlab='Difference')
hist(diff(disc.rates),breaks=100,main='Histogram of 1 Day Increments of Discount Rate',
     xlab='Difference')

###################################################################
# calculate correlations between the short rate and instantaneous #
# forward rates                                                   #
###################################################################

B1 <- function(x) {sum(Loading.1[,'b']*exp(-Loading.1[,'a']*x))}
B2 <- function(x) {sum(Loading.2[,'b']*exp(-Loading.2[,'a']*x))}
B3 <- function(x) {sum(Loading.3[,'b']*exp(-Loading.3[,'a']*x))}

sig2 <- diag(var(diff(PC[,1:3])))
B.mat <- matrix(c(B1(0),B2(0),B3(0),
                  B1(0.25),B2(0.25),B3(0.25),
                  B1(0.5),B2(0.5),B3(0.5),
                  B1(2),B2(2),B3(2),
                  B1(3),B2(3),B3(3),
                  B1(5),B2(5),B3(5),
                  B1(10),B2(10),B3(10),
                  B1(30),B2(30),B3(30),
                  sig2[1],sig2[2],sig2[3]),ncol=9)
rownames(B.mat) <- c('B1','B2','B3')
colnames(B.mat) <- c('0M','3M','6M','2Y','3Y','5Y','10Y','30Y','sig2')

# one factor model correlations
rho10 <- B.mat['B1','0M']*B.mat['B1','3M']/sqrt(B.mat['B1','0M']^2*B.mat['B1','3M']^2)
rho11 <- B.mat['B1','0M']*B.mat['B1','6M']/sqrt(B.mat['B1','0M']^2*B.mat['B1','6M']^2)
rho12 <- B.mat['B1','0M']*B.mat['B1','2Y']/sqrt(B.mat['B1','0M']^2*B.mat['B1','2Y']^2)
rho13 <- B.mat['B1','0M']*B.mat['B1','3Y']/sqrt(B.mat['B1','0M']^2*B.mat['B1','3Y']^2)
rho14 <- B.mat['B1','0M']*B.mat['B1','5Y']/sqrt(B.mat['B1','0M']^2*B.mat['B1','5Y']^2)
rho15 <- B.mat['B1','0M']*B.mat['B1','10Y']/sqrt(B.mat['B1','0M']^2*B.mat['B1','10Y']^2)
rho16 <- B.mat['B1','0M']*B.mat['B1','30Y']/sqrt(B.mat['B1','0M']^2*B.mat['B1','30Y']^2)
one.factor.rho <- c(rho10,rho11,rho12,rho13,rho14,rho15,rho16)

# two factor model correlations
B.mat.tmp <- B.mat[1:2,]
rho20 <- sum(B.mat.tmp[,'0M']*B.mat.tmp[,'3M']*B.mat.tmp[,'sig2'])/
  sqrt(sum(B.mat.tmp[,'0M']^2*B.mat.tmp[,'sig2'])*sum(B.mat.tmp[,'3M']^2*B.mat.tmp[,'sig2']))
rho21 <- sum(B.mat.tmp[,'0M']*B.mat.tmp[,'6M']*B.mat.tmp[,'sig2'])/
  sqrt(sum(B.mat.tmp[,'0M']^2*B.mat.tmp[,'sig2'])*sum(B.mat.tmp[,'6M']^2*B.mat.tmp[,'sig2']))
rho22 <- sum(B.mat.tmp[,'0M']*B.mat.tmp[,'2Y']*B.mat.tmp[,'sig2'])/
  sqrt(sum(B.mat.tmp[,'0M']^2*B.mat.tmp[,'sig2'])*sum(B.mat.tmp[,'2Y']^2*B.mat.tmp[,'sig2']))
rho23 <- sum(B.mat.tmp[,'0M']*B.mat.tmp[,'3Y']*B.mat.tmp[,'sig2'])/
  sqrt(sum(B.mat.tmp[,'0M']^2*B.mat.tmp[,'sig2'])*sum(B.mat.tmp[,'3Y']^2*B.mat.tmp[,'sig2']))
rho24 <- sum(B.mat.tmp[,'0M']*B.mat.tmp[,'5Y']*B.mat.tmp[,'sig2'])/
  sqrt(sum(B.mat.tmp[,'0M']^2*B.mat.tmp[,'sig2'])*sum(B.mat.tmp[,'5Y']^2*B.mat.tmp[,'sig2']))
rho25 <- sum(B.mat.tmp[,'0M']*B.mat.tmp[,'10Y']*B.mat.tmp[,'sig2'])/
  sqrt(sum(B.mat.tmp[,'0M']^2*B.mat.tmp[,'sig2'])*sum(B.mat.tmp[,'10Y']^2*B.mat.tmp[,'sig2']))
rho26 <- sum(B.mat.tmp[,'0M']*B.mat.tmp[,'30Y']*B.mat.tmp[,'sig2'])/
  sqrt(sum(B.mat.tmp[,'0M']^2*B.mat.tmp[,'sig2'])*sum(B.mat.tmp[,'30Y']^2*B.mat.tmp[,'sig2']))
two.factor.rho <- c(rho20,rho21,rho22,rho23,rho24,rho25,rho26)

# three factor model correlations
rho30 <- sum(B.mat[,'0M']*B.mat[,'3M']*B.mat[,'sig2'])/
  sqrt(sum(B.mat[,'0M']^2*B.mat[,'sig2'])*sum(B.mat[,'3M']^2*B.mat[,'sig2']))
rho31 <- sum(B.mat[,'0M']*B.mat[,'6M']*B.mat[,'sig2'])/
  sqrt(sum(B.mat[,'0M']^2*B.mat[,'sig2'])*sum(B.mat[,'6M']^2*B.mat[,'sig2']))
rho32 <- sum(B.mat[,'0M']*B.mat[,'2Y']*B.mat[,'sig2'])/
  sqrt(sum(B.mat[,'0M']^2*B.mat[,'sig2'])*sum(B.mat[,'2Y']^2*B.mat[,'sig2']))
rho33 <- sum(B.mat[,'0M']*B.mat[,'3Y']*B.mat[,'sig2'])/
  sqrt(sum(B.mat[,'0M']^2*B.mat[,'sig2'])*sum(B.mat[,'3Y']^2*B.mat[,'sig2']))
rho34 <- sum(B.mat[,'0M']*B.mat[,'5Y']*B.mat[,'sig2'])/
  sqrt(sum(B.mat[,'0M']^2*B.mat[,'sig2'])*sum(B.mat[,'5Y']^2*B.mat[,'sig2']))
rho35 <- sum(B.mat[,'0M']*B.mat[,'10Y']*B.mat[,'sig2'])/
  sqrt(sum(B.mat[,'0M']^2*B.mat[,'sig2'])*sum(B.mat[,'10Y']^2*B.mat[,'sig2']))
rho36 <- sum(B.mat[,'0M']*B.mat[,'30Y']*B.mat[,'sig2'])/
  sqrt(sum(B.mat[,'0M']^2*B.mat[,'sig2'])*sum(B.mat[,'30Y']^2*B.mat[,'sig2']))
three.factor.rho <- c(rho30,rho31,rho32,rho33,rho34,rho35,rho36)

plot(maturities,one.factor.rho,type='l',ylim=c(-1,1),main='Plot Between Short Rate and Instantaneous Forward Rates',
     ylab='Correlation',xlab='Maturity')
lines(maturities,two.factor.rho,col='red')
lines(maturities,three.factor.rho,col='blue')
legend('bottom',c("1 Factor","2 Factors",'3 Factors'),lty=c(1,1),col=c('black','red','blue'),cex=1)
