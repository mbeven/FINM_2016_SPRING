# Michael Beven
# University of Chicago - Financial Mathematics
# FINM33150 - Quantitative Strategies and Regression
# Homework 1 - Problem 3

# set working directory
setwd('/Users/michaelbeven/Documents/06_School/2016 Spring/FINM_2016_SPRING/FINM 33150/HW1')

# load key packages
library(MASS)
library(Quandl)
library(ggplot2)
library(stringr)
library(R.cache)
library(plotly)

# add memoization
reload.data <- TRUE
QLoad <- R.cache::addMemoization(Quandl::Quandl)

# load data
if (reload.data == TRUE) {
  Quandl.api_key('v21snmSix9KyXBWc1RkF')
  cat('Data Reload/n')
  msft.raw <- QLoad('YAHOO/MSFT')
  bac.raw <- QLoad('WIKI/BAC')
}

# take desired dates
msft <- subset(msft.raw, msft.raw$Date >= as.Date('2015-10-15') & 
                 msft.raw$Date <= as.Date('2015-11-09'))
bac <- subset(bac.raw, bac.raw$Date >= as.Date('2015-10-15') & 
                bac.raw$Date <= as.Date('2015-11-09'))

# add index code to data, so we don't confuse them
names(msft) <- paste('YAHOO.MSFT -',names(msft))
names(bac) <- paste('WIKI.BAC -',names(bac))
# fix renamed date column
names(msft)[1] <- 'Date'
names(bac)[1] <- 'Date'
# merge data
df <- merge(msft,bac)

# function to clean Quandl names
clean.quandl.name <- function(x) {
  cleaned <- x
  if (x=='Date') {
    
  } else {
    tryCatch({
      parts <- stringr::str_split(x, " - ",n=2)
      first.parts <- stringr::str_split(parts[[1]][[1]], "\\.",n=2)
      cleaned <- paste(first.parts[[1]][[2]], parts[[1]][[2]], sep=".")
      cleaned <- str_replace_all(cleaned," ","")
    },
    error = function(e) {cat(paste0("Err on",x,"\n"))}
    )
  }
  stringr::str_trim(cleaned)
}

# use clean.quandl.name
fixed.names <- lapply(names(df),clean.quandl.name)
cat(paste(fixed.names,sep="\n"))
df.renamed <- df
names(df.renamed) <- fixed.names

# only need close data
df.renamed.close <- subset(df.renamed, select=c('MSFT.Close','BAC.Close'))

# linear regression on close prices of MSFT vs. BAC
regress <- lm(df.renamed.close$MSFT.Close ~ df.renamed.close$BAC.Close)
print(summary(regress))

# create log returns data
N <- dim(df.renamed.close)[1]
df.logrets <- log(df.renamed.close[2:N,]) - log(df.renamed.close[1:N-1,])
regress.logrets <- lm(df.logrets$MSFT.Close ~ df.logrets$BAC.Close)
print(summary(regress.logrets))

# plot of regression of prices
pdf('RegPrices.pdf',width=10)
plot(df.renamed.close$BAC.Close,df.renamed.close$MSFT.Close,pch=20,ylim=c(45,60),
     xlim=c(15,20),xlab='BAC.Close',ylab='MSFT.Close',
     main='Regression of Microsoft Close Price Against Bank of America Close Price'
     )
abline(regress)
dev.off()

# plot of regression of returns
pdf('RegRets.pdf',width=10)
plot(df.logrets$BAC.Close,df.logrets$MSFT.Close,pch=20,xlab='BAC.Close',
     ylab='MSFT.Close',ylim=c(-0.02,0.1),xlim=c(-0.02,0.1),
     main='Regression of Microsoft Close Return Against Bank of America Close Return')
abline(regress.logrets)
dev.off()