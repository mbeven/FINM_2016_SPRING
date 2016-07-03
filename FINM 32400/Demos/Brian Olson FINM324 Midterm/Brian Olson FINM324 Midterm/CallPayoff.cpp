#include "CallPayOff.h"
#include <algorithm>

double CallPayoff::GetPayoff(double S) const
{
	return std::max(S - strike_, 0.0);
}

CallPayoff::CallPayoff(double strike)
	: Payoff(strike)
{}

CallPayoff::~CallPayoff()
{}