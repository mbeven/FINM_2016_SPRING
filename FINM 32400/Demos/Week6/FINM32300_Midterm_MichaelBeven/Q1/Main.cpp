#include "MonteCarlo.h"
#include <iostream>
using namespace std;

int main()
{
	// set number of simulations
	double N1 = 100;
	double N2 = 1000;
	double N3 = 10000;

	// initialise simulations
	MonteCarlo mc1(N1);
	MonteCarlo mc2(N2);
	MonteCarlo mc3(N3);

	cout << "N = 100: " << 4*mc1.MCValue() << endl; // multiply by 4, as per formula
	cout << "N = 1000: " << 4*mc2.MCValue() << endl;
	cout << "N = 10000: " << 4*mc3.MCValue() << endl; // note: by 10000 simulation our approximation of pi is almost 3.14
}