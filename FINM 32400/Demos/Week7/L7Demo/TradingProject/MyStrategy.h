#ifndef MY_STRATEGY_H
#define MY_STRATEGY_H

#include <quickfix/MessageCracker.h>
#include <quickfix/fix42/MarketDataRequest.h>
#include <quickfix/fix42/MarketDataRequestReject.h>
#include <quickfix/fix42/MarketDataSnapshotFullRefresh.h>
#include <quickfix/fix42/MarketDataIncrementalRefresh.h>
#include <quickfix/fix42/NewOrderSingle.h>
#include <quickfix/fix42/ExecutionReport.h>

#include <string>

#include "IdHelper.h"

using std::string;

enum OrderSide { BUY = '1', SELL = '2' };

#include <string>

using std::string;


class MyStrategy 
{
public:
	MyStrategy(const string& symbol, 
		const string& maturityMonthYear, 
		const string & account);
	

	// This callback is called once by Application to let us know that it is done initializing itself.
	void OnInit(FIX::SessionID mdSessionId, FIX::SessionID orderSessionId);
	
	// This callback is called by Application to let us know when the best bid changes.
	void OnBestBidUpdate(double qty, double px);

	// This callback is called by Application to let us know when the best offer changes.
	void OnBestOfferUpdate(double qty, double px);

	// This callback is called by Application whenever the trade ticker changes
	void OnLastTradeUpdate(double qty, double px);

	// This callback is called by Application to let us know that an order was filled.
	void OnOrderFill(OrderSide side, double qty, double px);

	// This callback is called by Application to let us know that an order was rejected.
	void OnOrderReject(OrderSide side, double qty);

	// Subscribe to market data updates for an instrument.
	void SendMarketDataSubscription(const string& symbol, const string& maturityMonthYear);

	// Send a market order
	void SendMarketOrder(const std::string & symbol,
		const string& maturityMonthYear, const string& account,
		OrderSide side, int qty);

	// Get Current PnL
	double PnL();
	
private:
	FIX::SessionID mdSessionId_;
	FIX::SessionID orderSessionId_;

	const string symbol_;
	const string maturityMonthYear_;
	const string account_;

};

#endif