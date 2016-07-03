#include "BinomialTree.h"

#include <iostream>
#include <omp.h>

using std::cout;
using std::endl;


BinomialTree::BinomialTree(double S, double r, double q, double v, double T, int N)
	: S(S), r(r), q(q), v(v), T(T), N(N),  treeInitialized_(false)
{
	dt = T / N;
	initializeTree();
}

void BinomialTree::initializeTree()
{
	//Step 1
	//Create/initialize the Tree

	//we have N+1 time steps i.e. N+1 VerticalNodes
	tree_.resize(N + 1);

	//each VerticalNodes vector should have (i+1) Nodes where i is 
	//the time index
	for (long i = 0; i <= N; ++i)
	{
		tree_[i].resize(i + 1);
	}

	//Step 2
	//Populate stock prices
	//we access the first and second elements in a pair using first and second fields
	tree_[0][0].first = S;

	double nu = (r - q - 0.5*v*v);
	double sqrt_dt = sqrt(dt);
	double u = exp(v*sqrt_dt);

	//i is horizontal time index
	// we go from left to right
	for (long i = 1; i <= N; ++i)
	{
		//Eqn 6
		//St(D, t+dt) = St*exp((nu)dt - sigma*sqrt(dt)), where nu = r-q-0.5*sigma*sigma
		tree_[i][0].first = tree_[i - 1][0].first / u;

		for (int j = 1; j <= i; ++j)
		{
			tree_[i][j].first = tree_[i][0].first * pow(u, 2 * j);
		};
	}

	treeInitialized_ = true;
}

double BinomialTree::Price(const Option &theOption)
{
	if (!treeInitialized_) initializeTree();

	//Step 3
	//Calculate option prices at t=T
	double sqrt_dt = sqrt(dt);
	double u = exp(v*sqrt_dt);
	double p_u = (exp(r*dt) - (1 / u)) / (u - (1 / u));
	double p_d = 1 - p_u;

	for (long j = 0; j <= N; ++j)
	{
		
		tree_[N][j].second = theOption.ExpirationPayoff(tree_[N][j].first);
	}

	//Step 4
	//Back propagation
	//ir is index i in reverse direction
	double disc = exp(-r*dt);
	for (long ir = N - 1; ir >= 0; --ir)
	{
		for (long j = 0; j <= ir; ++j)
		{
			//use Equation 8 to find the discounted expectation of the two adjacent option prices
			double discountedExpectation = (p_d*tree_[ir + 1][j].second + p_u*tree_[ir + 1][j + 1].second)*disc;	/*CRR*/

			//find the payoff at the node.
			//if the option is european, the intermediate payoff is the same as discounted expectation
			//if the option is american, the intermediate payoff is the more profitable value between 
			//immediate exercise and discounted expectation
			tree_[ir][j].second = theOption.IntermediatePayoff(tree_[ir][j].first, discountedExpectation);
		}
	}

	return tree_[0][0].second;
}