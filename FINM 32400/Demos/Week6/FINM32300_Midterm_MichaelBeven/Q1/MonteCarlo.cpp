#include "MonteCarlo.h"
#include <cmath>
#include <math.h>

//construct params
MonteCarlo::MonteCarlo(const int& _num_sim)
{
	num_sim = _num_sim;
}

//destructor
MonteCarlo::~MonteCarlo() {}

//in or out of the circle function
int InOrOut(double x, double y)
{
	if (sqrt(x*x + y*y) < 1) // checking distance of coordinate from zero
	{
		return 1;
	}
	else
	{
		return 0;
	}
}

double MonteCarlo::MCValue()
{
	int z = 0;
	double sum = 0.0;

	for (int i = 0; i < num_sim; i++)
	{
		double x = static_cast<double>(std::rand()) / RAND_MAX; // rand[0,1]
		double y = static_cast<double>(std::rand()) / RAND_MAX; // rand[0,1]

		int z = InOrOut(x, y); // use the function set above
		sum = sum + z; // build up a sum of points found within circle
	}
	return (sum/num_sim); // take the ratio to get pi/4
}