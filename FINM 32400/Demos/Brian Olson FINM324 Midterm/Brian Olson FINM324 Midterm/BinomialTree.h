#ifndef BINOMIAL_TREE_H
#define BINOMIAL_TREE_H

#include <vector>
#include "Option.h"

using std::vector;
using std::pair;

class BinomialTree
{
public:
	BinomialTree(double S, double r, double q, double v, double T, int N); //Constructor

	double Price(const Option& option); //Pricing function that takes option as input

private:
	//Tree initialization function/variable
	void initializeTree();
	bool treeInitialized_;

	//Build tree with stock price and option price at each node
	typedef double StockPrice;
	typedef double OptionPrice;
	typedef pair<StockPrice, OptionPrice> Node;
	typedef vector<Node> VerticalNodes;
	typedef vector<VerticalNodes> Tree;

	//Binomial tree variable
	Tree tree_;

	//Variables required for tree
	double S;
	double r;
	double q;
	double v;
	double T;
	int N;
	double dt;

};

#endif