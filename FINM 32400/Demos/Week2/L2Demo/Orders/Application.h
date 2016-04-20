
#ifndef TRADECLIENT_APPLICATION_H
#define TRADECLIENT_APPLICATION_H

#include <quickfix/Application.h>
#include <quickfix/MessageCracker.h>
#include <quickfix/Values.h>
#include <quickfix/Mutex.h>

#include <quickfix/fix42/NewOrderSingle.h>
#include <quickfix/fix42/ExecutionReport.h>
#include <quickfix/fix42/MarketDataRequest.h>
#include <quickfix/fix42/MarketDataRequestReject.h>
#include <quickfix/fix42/MarketDataSnapshotFullRefresh.h>
#include <quickfix/fix42/MarketDataIncrementalRefresh.h>

#include <quickfix/fix42/OrderCancelRequest.h>
#include <quickfix/fix42/OrderCancelReject.h>
#include <quickfix/fix42/OrderCancelReplaceRequest.h>

#include <quickfix/Application.h>
#include <quickfix/MessageCracker.h>
#include <quickfix/FileLog.h>
#include <quickfix/FileStore.h>
#include <quickfix/SocketInitiator.h>

#include <string>
#include <queue>

#include "IdHelper.h"

using std::string;

class Application : public FIX::Application, 
	public FIX::MessageCracker
{
public:
	Application(string& configFile);

	~Application();

	void Init();

	void Run();

private:
	void sendMarketOrder();
	void sendLimitOrder();
	void sendCancelOrder();
	void sendCancelReplaceOrder();
	char queryAction();

	//QF Callbacks we use
	void onMessage(const FIX42::ExecutionReport&, const FIX::SessionID&);

	//QF Callbacks we don't discuss in detail
	void onCreate( const FIX::SessionID& );
	void onLogon( const FIX::SessionID& sessionID );

	void onLogout( const FIX::SessionID& sessionID );

	void toAdmin(FIX::Message&, const FIX::SessionID&);

	void fromAdmin(const FIX::Message&, const FIX::SessionID&) 
		throw(FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::RejectLogon);
	
	void toApp( FIX::Message&, const FIX::SessionID&) throw( FIX::DoNotSend );
	
	void fromApp( const FIX::Message& message, const FIX::SessionID& sessionID ) 
		throw( FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::UnsupportedMessageType );

	string configFile_;

	FIX::SessionID orderSessionId_;
	FIX::MessageStoreFactory* messageStoreFactory_;
	FIX::FileLogFactory* logFactory_;
	FIX::SessionSettings* sessionSettings_;
	FIX::SocketInitiator* initiator_;

	std::string mySenderCompId_;

};

#endif
