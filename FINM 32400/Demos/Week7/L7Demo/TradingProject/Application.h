#ifndef Application_H
#define Application_H

#include <string>
#include <iostream>
#include <quickfix/Application.h>
#include <quickfix/MessageCracker.h>
#include <quickfix/FileLog.h>
#include <quickfix/FileStore.h>
#include <quickfix/SocketInitiator.h>
#include <quickfix/fix42/MarketDataRequest.h>
#include <quickfix/fix42/MarketDataRequestReject.h>
#include <quickfix/fix42/MarketDataSnapshotFullRefresh.h>
#include <quickfix/fix42/MarketDataIncrementalRefresh.h>
#include <quickfix/fix42/NewOrderSingle.h>
#include <quickfix/fix42/ExecutionReport.h>
#include "IdHelper.h"
#include "MyStrategy.h"


// A Application interface that allows our Strategy to subscribe to market data and send orders.
class Application : public FIX::Application,
              public FIX::MessageCracker
{
public:
	Application(const MyStrategy& strategy);
	~Application();

	// Establish FIX connections and do any other setup.
	void Init(const std::string & configFile);

private: 
	// QF callbacks
	void onMessage(const FIX42::ExecutionReport&, const FIX::SessionID&);
	void onMessage(const FIX42::MarketDataSnapshotFullRefresh&, const FIX::SessionID&);
	void onMessage(const FIX42::MarketDataIncrementalRefresh& msg, const FIX::SessionID&);
	void onMessage(const FIX42::MarketDataRequestReject&, const FIX::SessionID&);

	// More QF callbacks
	void onCreate(const FIX::SessionID&);
	void onLogon(const FIX::SessionID&);
	void onLogout(const FIX::SessionID&);
	void toAdmin(FIX::Message&, const FIX::SessionID&);
	void toApp(FIX::Message&, const FIX::SessionID&) throw(FIX::DoNotSend);
	void fromAdmin(const FIX::Message&, const FIX::SessionID&) throw(FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::RejectLogon);
	void fromApp(const FIX::Message& message, const FIX::SessionID& sessionID) throw(FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::UnsupportedMessageType);
	
	MyStrategy strategy_;
	
	FIX::SessionID mdSessionId_;
	FIX::SessionID orderSessionId_;

	FIX::MessageStoreFactory* messageStoreFactory_;
	FIX::FileLogFactory* logFactory_;
	FIX::SessionSettings* sessionSettings_;
	FIX::SocketInitiator* initiator_;
};


#endif