#ifndef CALL_PAYOFF_H
#define CALL_PAYOFF_H

#include "PayOff.h"

class CallPayoff : public Payoff
{
public:
	CallPayoff(double strike); //Constructor

	~CallPayoff(); //Destructor

	double GetPayoff(double) const; //Derived GetPayoff Specification

};

#endif