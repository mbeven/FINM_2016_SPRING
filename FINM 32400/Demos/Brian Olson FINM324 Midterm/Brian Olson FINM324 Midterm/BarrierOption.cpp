#include "BarrierOption.h"

//Constructor
BarrierOption::BarrierOption(double expiry, const shared_ptr<Payoff>& payoff,double barrier)
	: Option(expiry, payoff), barrier(barrier)
{}

//Expiration payoff - set to zero if above the up and out barrier
double BarrierOption::ExpirationPayoff(double S) const
{
	if (S > barrier)
	{
		return 0;
	}
	else
	{
		return payoff_->GetPayoff(S);
	}
}

//Intermediate payoff - set to zero if above the up and out barrier
double BarrierOption::IntermediatePayoff(double S, double discountedExpectation)  const
{
	if (S > barrier)
	{
		return 0;
	}
	else
	{
		return discountedExpectation;
	}
}