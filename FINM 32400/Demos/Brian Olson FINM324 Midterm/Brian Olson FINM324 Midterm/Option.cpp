#include "Option.h"

Option::Option(double T, const shared_ptr<Payoff>& payoff)
	: T_(T)
{
	payoff_ = payoff;
}

double Option::GetExpiry() const
{
	return T_;
}