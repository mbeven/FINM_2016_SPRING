#ifndef PAYOFF_H
#define PAYOFF_H

class Payoff
{
public:
	Payoff(double strike); //Constuctor

	virtual double GetPayoff(double) const = 0; //Virtual function to be defined in derived classes

protected:
	double strike_;

};

#endif