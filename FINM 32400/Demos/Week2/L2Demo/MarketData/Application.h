#ifndef TRADECLIENT_APPLICATION_H
#define TRADECLIENT_APPLICATION_H

#include "IdHelper.h"

#include <quickfix/Application.h>
#include <quickfix/MessageCracker.h>
#include <quickfix/FileLog.h>
#include <quickfix/FileStore.h>
#include <quickfix/SocketInitiator.h>

#include <quickfix/Values.h>
#include <quickfix/Mutex.h>

#include <quickfix/fix42/NewOrderSingle.h>
#include <quickfix/fix42/ExecutionReport.h>
#include <quickfix/fix42/OrderCancelRequest.h>
#include <quickfix/fix42/OrderCancelReject.h>
#include <quickfix/fix42/OrderCancelReplaceRequest.h>
#include <quickfix/fix42/MarketDataRequest.h>

#include <string>

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
  void sendMarketDataRequest();

  char queryAction();

  //QF callbacks we use (and discuss)
  void onMessage(const FIX42::MarketDataSnapshotFullRefresh& message, 
	  const FIX::SessionID&);
  void onMessage(const FIX42::MarketDataIncrementalRefresh& message, 
	  const FIX::SessionID&);

  //QF callbacks we don't discuss in detail
  void onCreate( const FIX::SessionID& );
  void onLogon( const FIX::SessionID& sessionID );
  void onLogout( const FIX::SessionID& sessionID );
  void toAdmin(FIX::Message&, const FIX::SessionID&);
  void fromAdmin(const FIX::Message&, const FIX::SessionID&) throw(FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::RejectLogon);
  void toApp(FIX::Message&, const FIX::SessionID& ) throw( FIX::DoNotSend );
  void fromApp( const FIX::Message& message, const FIX::SessionID& sessionID ) throw( FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::UnsupportedMessageType );
  
  FIX::MessageStoreFactory* messageStoreFactory_;
  FIX::FileLogFactory* logFactory_;
  FIX::SessionSettings* sessionSettings_;
  FIX::SocketInitiator* initiator_;
  FIX::SessionID mdSessionId_;

  string configFile_;

};

#endif
