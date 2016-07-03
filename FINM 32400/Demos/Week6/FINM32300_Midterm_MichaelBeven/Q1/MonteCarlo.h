#ifndef _MonteCarlo_H
#define _MonteCarlo_H

using namespace std;
#include<cmath>

class MonteCarlo
{
public:
	//construct params
	MonteCarlo(const int& _num_sim);

	//destructor
	~MonteCarlo();
	//monte carlo sim
	double MCValue();
	//params (only number of simulations here, given dimensions of circle/square
	int num_sim;
};
#endif
