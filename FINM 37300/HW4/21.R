# problem 21

# set parameters for Garman Kolhagen formula
days = as.numeric(difftime(strptime("11.10.2016", format = "%d.%m.%Y"),
               strptime("11.04.2016", format = "%d.%m.%Y"),units="days")) # trade date to expiry date
tau = days/365
r_AUD = 0.0215 # aud deposit rate
r_USD = 0.0038 # usd deposit rate
AUD_ACT = 365 # day count convention
USD_ACT = 360 # day count convention
sig = 0.128 # implied volatility
K = 0.7400 # strike
S = 0.7540 # spot
notional = 5*10^7 # notional amount

# implement GK formula
Pd = 1/(1+r_USD*days/USD_ACT) # present value of usd
Fwd = S*((1+r_USD*days/USD_ACT)/(1+r_AUD*days/AUD_ACT)) # forward
d1 = (log(Fwd/K) + 0.5*sig^2*tau)/(sig*sqrt(tau))
d2 = (log(Fwd/K) - 0.5*sig^2*tau)/(sig*sqrt(tau))
w = -1 # call or put toggle
p = Pd*w*(Fwd*pnorm(w*d1)-K*pnorm(w*d2)) # price 
pnumccy = p
print(pnumccy)

# USD premium
cat('USD premium: ', notional*p)

# USD pips
cat('USD pips:', 1*10^4*pnumccy)

# USD %
cat('USD %:', 100*pnumccy/K)

# AUD premium
cat('AUD premium: ', notional*p/S)

# AUD pips
cat('AUD pips:', 1*10^4*pnumccy/K/S)

# AUD %
cat('AUD %:', 100*pnumccy/S)
