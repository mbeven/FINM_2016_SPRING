#include "MCPricer.h"
#include "RandomNumberGenerator.h"

#include <cmath>
#include <algorithm>
#include <vector>
#include <omp.h>
#include <mutex>
#include <numeric>

OptionPrice MCPricer::MCPrice(EuropeanOption& option, StockPrice S0, Volatility sigma, Rate r, unsigned long M)
{
	RandomNumberGenerator::SetSeed();

	double runningSum = 0.0;

	double T = option.GetExpiry();

	for (int i = 0; i < M; ++i)
	{
		double z_i = RandomNumberGenerator::RandomByBoxMuller();

		double ST_i = S0*exp((r - sigma*sigma / 2.0)*T + sigma*z*sqrt(T));

		runningSum += option.OptionPayOff(ST_i);
	}

	//return discounted price
	return exp(-r*T)*(runningSum / M);
}


OptionPrice MCPricer::MCPrice(EuropeanOption& option, StockPrice S0, Volatility sigma, Rate r, unsigned long M)
{
	RandomNumberGenerator::SetSeed();

	double runningSum = 0.0;
	std::vector<double> z(M);
	for (int i = 0; i<M; ++i)
	{
		z[i] = RandomNumberGenerator::RandomByBoxMuller();
	}
	double T = option.GetExpiry();

	//std::mutex m;

	std::vector<double> payoffs(M);

	#pragma omp parallel for
	for (int i = 0; i < M; ++i)
	{
		//double z_i = RandomNumberGenerator::RandomByBoxMuller();

		double ST_i = S0*exp((r - sigma*sigma / 2.0)*T + sigma*z[i]*sqrt(T));

		payoffs[i] = option.OptionPayOff(ST_i);

		//std::lock_guard<std::mutex> lock(m); removes race condition, but is very slow
		//runningSum += option.OptionPayOff(ST_i); //race condition here
	}
	#pragma omp barrier;

	runningSum = accumulate(payoffs.begin(), payoffs.end(), 0.0);

	//return discounted price
	return exp(-r*T)*(runningSum / M);
}


