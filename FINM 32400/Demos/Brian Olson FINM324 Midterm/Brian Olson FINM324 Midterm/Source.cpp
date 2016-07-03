#include "CallPayoff.h"
#include "BinomialTree.h"
#include "BarrierOption.h"
#include <iostream>

#include <memory>
using std::shared_ptr;

int main()
{
	double T = 1.0; //Expiry
	double K = 100.0; //Strike
	double S = 100.0; //Stock Price
	double v = 0.3; //Volatility
	double r = 0.02; //Risk free rate
	double q = 0.00; //Dividend rate

	int N = 1000; //Number of periods in the tree
	int barrier = 110.00; //Barrier at which the option ceases to exist

	//Create payoffs for each option
	shared_ptr<Payoff> callPayoff = std::make_shared<CallPayoff>(K);

	//Create options for each payoff
	BarrierOption UpAndOutBarrier (T, callPayoff,barrier);

	//Create binomial tree
	BinomialTree tree(S, r, q, v, T, N); //Create single instance of the binomial tree

	//Value up and out barrier call and output results
	double CallPriceTree = tree.Price(UpAndOutBarrier);
	std::cout << "Up and Out Barrier Call Price (Tree): " << CallPriceTree << std::endl;

}