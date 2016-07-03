#ifndef BARRIER_OPTION_H
#define BARRIER_OPTION_H

#include "Option.h"
#include "Payoff.h"

#include <memory>
using std::shared_ptr;

//Assumes up and out barrier option
class BarrierOption : public Option
{
public:
	BarrierOption(double T, const shared_ptr<Payoff>& payoff,double barrier); //Constructor

	virtual double ExpirationPayoff(double S) const; //Retrieves expiration payoff

	virtual double IntermediatePayoff(double S, double discountedExpectation) const; //Retrieves intermediate timestep payoff

	double barrier;

};

#endif