#include "BinomialTree.h"

#include <iostream>
#include <omp.h>

using std::cout;
using std::endl;


BinomialTree::BinomialTree(double S, double rate, double div, double time, double vol, double expiry, int steps)
	: S0(S),
	  r(rate),
	  q(div),
	  v(vol),
	  T(time),
	  N(steps),
	  treeInitialized_(false)
{
#pragma region precalculations
	dt = T / N;
	nu = r - q - 0.5*v*v;
	disc = exp(-r*dt);

	sqrt_dt = sqrt(dt);
#pragma endregion

	buildTree();

}

void BinomialTree::buildTree()
{
#pragma region Step 1
	//Create/initialize the Tree
	
	//we have N+1 time steps i.e. N+1 VerticalNodes
	tree_.resize(N + 1);

	//each VerticalNodes vector should have (i+1) Nodes where i is 
	//the time index
	for (long i = 0; i <= N; ++i)
	{
		tree_[i].resize(i + 1);
	}
#pragma endregion

#pragma region Step 2
	//Populate stock prices
	//we access the first and second elements in a pair using first and second fields
	tree_[0][0].first = S0;

	//i is horizontal time index
	// we go from left to right
	for (long i = 1; i <= N; ++i)
	{
		//Eqn 6
		//St(D, t+dt) = St*exp((nu)dt - sigma*sqrt(dt)), where nu = r-0.5*sigma*sigma
		tree_[i][0].first = tree_[i = 1][0].first*exp(nu*dt - v*sqrt_dt);
		# pragma omp parallel for
		for (int j = 1; j <= i; ++j)
		{
			tree_[i][j].first = tree_[i][0].first*exp(j * 2 * v*sqrt_dt);
		}
		#pragma omp barrier
	}

	treeInitialized_ = true;
#pragma endregion
}

double BinomialTree::Price(const Option &theOption)
{
	if (!treeInitialized_) buildTree();

#pragma region Step 3
	//Calculate option prices at t=T
	#pragma omp parallel for
	for (long j = 0; j <= N; ++j)
	{
		tree_[N][j].second = theOption.ExpirationPayoff(tree_[N][j].first);
	}
	#pragma omp barrier
#pragma end region

#pragma region Step 4
	//Back propagation
	//ir is index i in reverse direction
	for (long ir = N - 1; ir >= 0; --ir)
	{
		#pragma omp parallel for
		for (long j = 0; j <= ir; ++j)
		{
			//use Equation 8 to find the discounted expectation of the two adjacent option prices
			double discountedExpectation = disc*0.5*(tree_[ir + 1][j].second + tree_[ir + 1][j + 1].second);
			
			//find the payoff at the node: 
			//  a)euroepan: the intermediate payoff is the same as discounted expectation
			//  b)american: the intermediate payoff is the more profitable value between 
			//  immediate exercise and discounted expectation
			//  c)barrier: we have to see if the barrier is hit and use appropriate in/out rules
			tree_[ir][j].second = theOption.IntermediatePayoff(tree_[ir][j].first, discountedExpectation);
		}
		#pragma omp barrier
	}
#pragma endregion
	return tree_[0][0].second;
}


