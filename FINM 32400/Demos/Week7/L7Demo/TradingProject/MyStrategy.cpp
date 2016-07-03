#include "MyStrategy.h"


MyStrategy::MyStrategy(const string& symbol,
	const string& maturityMonthYear,
	const string& account)
	: symbol_(symbol),
	maturityMonthYear_(maturityMonthYear),
	account_(account)
{ }

void MyStrategy::OnInit(FIX::SessionID mdSessionId, FIX::SessionID orderSessionId)
{
	mdSessionId_ = mdSessionId;
	orderSessionId_ = orderSessionId;

	SendMarketDataSubscription(symbol_, maturityMonthYear_);
}


void MyStrategy::OnBestBidUpdate(double qty, double px)
{
	std::cout << "MarketDataUpdate: BID " << px << " / " << qty << std::endl;

	//Incomplete
}

void MyStrategy::OnBestOfferUpdate(double qty, double px)
{
	std::cout << "MarketDataUpdate: OFFER " << px << " / " << qty << std::endl;

	//Incomplete
}

void MyStrategy::OnLastTradeUpdate(double qty, double px)
{
	std::cout << "MarketDataUpdate: Last Trade " << px << " / " << qty << std::endl;

	//Incomplete

}

void MyStrategy::OnOrderFill(OrderSide side, double qty, double px)
{
	std::cout << std::endl << "FILL: side=" << side << ", price=" << px << ", qty=" << qty << std::endl;

	//Incomplete 
}

void MyStrategy::OnOrderReject(OrderSide side, double qty)
{
	// The order was rejected -- you may want to update your working quantity

	//Incomplete
}


void MyStrategy::SendMarketDataSubscription(const string& symbol,
	const std::string & maturityMonthYear)
{
	//Incomplete


	//FIX::Session::sendToTarget(msg, mdSessionId_);
}

void MyStrategy::SendMarketOrder(const string& symbol,
	const std::string & maturityMonthYear,
	const std::string & account,
	OrderSide side, int qty)
{
	//FIX42::NewOrderSingle msg;

	//Incomplete

	//FIX::Session::sendToTarget(msg, orderSessionId_);
}

double MyStrategy::PnL()
{
	//Incomplete
	return 0.0;
}