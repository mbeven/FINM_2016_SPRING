#ifndef BINOMIAL_TREE_H
#define BINOMIAL_TREE_H

#include "Option.h"
#include <vector>

using std::vector;
using std::pair;

class BinomialTree
{
public:
	BinomialTree(double S, double rate, double div, double time, double vol, double expiry, int steps);

	double Price(const Option& option);

private:
	void buildTree();
	bool treeInitialized_;

	typedef double StockPrice;
	typedef double OptionPrice;
	typedef pair<StockPrice, OptionPrice> Node;
	typedef vector<Node> VerticalNodes;
	typedef vector<VerticalNodes> Tree;
	
	Tree tree_;

	double S0;
	double r;
	double q;
	double v;
	double T;
	double N;

	double dt;
	double nu;
	double disc;
	double sqrt_dt;

};

#endif