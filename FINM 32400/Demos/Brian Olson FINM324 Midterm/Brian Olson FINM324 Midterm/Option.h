#ifndef OPTION_H
#define OPTION_H

#include <memory>
#include "Payoff.h"

using std::shared_ptr;

class Option
{
public:
	Option(double T, const shared_ptr<Payoff>& payoff); //Constructor

	virtual double ExpirationPayoff(double S) const = 0; //Virtual ExpirationPayoff function to be declared in derived class

	virtual double IntermediatePayoff(double S, double discountedExpectation) const = 0; //Virtual IntermediatePayoff function to be declared in derived class

	double GetExpiry() const; //Gets expiry of option

protected:
	shared_ptr<Payoff> payoff_; //Payoff pointer

private:
	double T_;

};

#endif