//Thanks to Mike Gatney (Connamara Systems) for QF tips and documentation

#include "Application.h"

#include <quickfix/Session.h>
#include <quickfix/fix42/MarketDataIncrementalRefresh.h>
#include <quickfix/fix42/MarketDataSnapshotFullRefresh.h>

#include <iostream>
#include <sstream>

using std::string;
using std::cout;
using std::endl;

Application::Application(string& configFile)
	: configFile_(configFile)
{
}

Application::~Application()
{
	if (initiator_) initiator_->stop();
	delete initiator_;
	delete logFactory_;
	delete messageStoreFactory_;
	delete sessionSettings_;
}

// Establish FIX connections and do any other setup.
void Application::Init()
{
	// Boilerplate quickfix setup:
	sessionSettings_ = new FIX::SessionSettings(configFile_);
	messageStoreFactory_ = new FIX::FileStoreFactory(*sessionSettings_);
	logFactory_ = new FIX::FileLogFactory(*sessionSettings_);
	initiator_ = new FIX::SocketInitiator(*this, 
							*messageStoreFactory_, 
							*sessionSettings_, 
							*logFactory_);
	initiator_->start();
	
	// Logging on to market data (prices) FIX session
	for(int i = 0; i < 3; ++i)
	{
		FIX::Session* mdSession = FIX::Session::lookupSession(mdSessionId_);
		if(mdSession)
		{
			if(mdSession->isLoggedOn()) return;
		}

		std::cout << "[init] Waiting for all FIX Sessions to logon..." << std::endl;
		FIX::process_sleep(2);
	}

	throw std::runtime_error("[init] Fatal error: timed out waiting for all FIX Sessions to logon!");
}


void Application::Run()
{
	bool keepRunning = true;

	while (keepRunning)
	{
		try
		{
			char action = queryAction();

			switch (action)
			{
			case '0':
				keepRunning = false;
				break;

			case '1':
				sendMarketDataRequest();
				break;
			}
		}
		catch (std::exception& e)
		{
			std::cout << "Message Not Sent: " << e.what();
		}
	}
}

char Application::queryAction()
{
	char value;
	std::cout << std::endl
		<< "1) Market Data Request" << std::endl
		<< "0) Quit" << std::endl
		<< "Action: ";

	std::cin >> value;

	return value;
}

//https://www.tradingtechnologies.com/help/fix-adapter-reference/market-data-request-v/

void Application::sendMarketDataRequest()
{
	FIX42::MarketDataRequest msg;

	msg.set(FIX::MDReqID(IdHelper::GetNextMDRequestId()));
	msg.set(FIX::SubscriptionRequestType(FIX::SubscriptionRequestType_SNAPSHOT_PLUS_UPDATES));
	msg.set(FIX::MarketDepth(1));
	msg.set(FIX::MDUpdateType(FIX::MDUpdateType_INCREMENTAL_REFRESH));
	msg.set(FIX::AggregatedBook(FIX::AggregatedBook_YES));

	// We want best bid, best offer, and last trade notifications
	FIX42::MarketDataRequest::NoMDEntryTypes marketDataEntryGroup;
	marketDataEntryGroup.set(FIX::MDEntryType(FIX::MDEntryType_BID));
	msg.addGroup(marketDataEntryGroup);
	marketDataEntryGroup.set(FIX::MDEntryType(FIX::MDEntryType_OFFER));
	msg.addGroup(marketDataEntryGroup);
	marketDataEntryGroup.set(FIX::MDEntryType(FIX::MDEntryType_TRADE));
	msg.addGroup(marketDataEntryGroup);

	msg.set(FIX::NoRelatedSym(1));

	// Repeating group for the instrument to which we are subscribing:
	//group 1
	FIX42::MarketDataRequest::NoRelatedSym symbolGroup1;
	symbolGroup1.set(FIX::Symbol("ES"));
	symbolGroup1.set(FIX::MaturityMonthYear("201606"));
	symbolGroup1.set(FIX::SecurityExchange("CME"));
	symbolGroup1.set(FIX::SecurityType("FUT"));
	msg.addGroup(symbolGroup1);

	//group 2
	/*
	FIX42::MarketDataRequest::NoRelatedSym symbolGroup2;
	symbolGroup2.set(FIX::Symbol("ES"));
	symbolGroup2.set(FIX::MaturityMonthYear("201612"));
	symbolGroup2.set(FIX::SecurityExchange("CME"));
	symbolGroup2.set(FIX::SecurityType("FUT"));
	msg.addGroup(symbolGroup2);
	*/

	FIX::Session::sendToTarget(msg, mdSessionId_);
}

/////////////////////////
// Callback Methods
/////////////////////////

//https://www.tradingtechnologies.com/help/fix-adapter-reference/market-data-snapshotfull-refresh-w/

void Application::onMessage(const FIX42::MarketDataSnapshotFullRefresh& msg,
	const FIX::SessionID&)
{
	FIX::MDReqID id;
	msg.get(id);

	FIX::NoMDEntries noMDEntries;
	msg.get(noMDEntries);
	for (int i = 1; i <= noMDEntries; ++i)
	{
		FIX42::MarketDataSnapshotFullRefresh::NoMDEntries group;
		FIX::MDEntryType type;
		FIX::MDEntryPx px;
		FIX::MDEntrySize qty;
		
		msg.getGroup(i, group);
		group.get(type);
		group.get(px);
		group.get(qty);
		
		if (FIX::MDEntryType_BID == type.getValue())
		{
			cout << "id: " << id << ", bid: " << qty.getValue() << ", " << px.getValue() << endl;
		}
		else if (FIX::MDEntryType_OFFER == type.getValue())
		{
			cout << "id: " << id << ", offer: " << qty.getValue() << ", " << px.getValue() << endl;
		}
		else if (FIX::MDEntryType_TRADE == type.getValue())
		{
			cout << "id: " << id << ", trade: " << qty.getValue() << ", " << px.getValue() << endl;
		}
		else
		{
			std::cout << "Unknown MDEntryType: " << type << std::endl;
		}
	}
}

//https://www.tradingtechnologies.com/help/fix-adapter-reference/market-data---incremental-refresh-x/

void Application::onMessage(const FIX42::MarketDataIncrementalRefresh& msg, const FIX::SessionID&)
{
	FIX::MDReqID id;
	msg.get(id);

	FIX::NoMDEntries noMDEntries;
	msg.get(noMDEntries);
	for (int i = 1; i <= noMDEntries; ++i)
	{
		FIX42::MarketDataIncrementalRefresh::NoMDEntries group;
		FIX::MDEntryType type;
		FIX::MDEntryPx px;
		FIX::MDEntrySize qty;
		FIX::MDUpdateAction action;

		msg.getGroup(i, group);
		group.get(type);
		group.get(px);
		group.get(qty);
		group.get(action);

		if (FIX::MDUpdateAction_NEW == action.getValue() || 
			FIX::MDUpdateAction_CHANGE == action.getValue())
		{
			if (FIX::MDEntryType_BID == type.getValue())
			{
				cout << "id: " << id <<  ", bid: " << qty.getValue() << ", " << px.getValue() << endl;
			}
			else if (FIX::MDEntryType_OFFER == type.getValue())
			{
				cout << "id: " << id << ", offer: " << qty.getValue() << ", " << px.getValue() << endl;
			}
			else if (FIX::MDEntryType_TRADE == type.getValue())
			{
				cout << "id: " << id << ", trade: " << qty.getValue() << ", " << px.getValue() << endl;
			}
			else
			{
				std::cout << "Unknown MDEntryType: " << type << std::endl;
			}
		}
	}
}

void Application::fromApp(const FIX::Message& message, const FIX::SessionID& sessionId)
throw(FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::UnsupportedMessageType)
{
	crack(message, sessionId);
}

void Application::onCreate(const FIX::SessionID& sessionId)
{
	mdSessionId_ = sessionId;
}

void Application::onLogon( const FIX::SessionID& sessionId )
{
	// Ask QF for the SessionSettings for this Session
	const FIX::Dictionary* settings = initiator_->getSessionSettings(sessionId);

	// Grab our custom "MyMarketDataSession" parameter (if it exists) from the SessionSettings
	if(settings->has("MyMarketDataSession") && settings->getBool("MyMarketDataSession"))
	{
		mdSessionId_ = sessionId;
		std::cout << "[onLogon] " << mdSessionId_ << " (MyMarketDataSession)" << std::endl;
	}
}

void Application::onLogout( const FIX::SessionID&)
{
}

void Application::fromAdmin( const FIX::Message&, const FIX::SessionID& ) 
	throw( FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::RejectLogon )
{}


void Application::toAdmin( FIX::Message& message, const FIX::SessionID& sessionId) 
{
	// First we have to figure out what the message is
	// Remember: Msgtype is in the header, not the body!
	FIX::MsgType msgType;
	message.getHeader().getField(msgType);
	
	// Tip: right-click 'FIX::MsgType_Logon' and select 'Go To Definition' to see other useful contants that QF defines for you.
	// Tip: hover your mouse cursor over 'FIX::MsgType_Logon' to see its value.
	if(FIX::MsgType_Logon == msgType)
	{
		const FIX::Dictionary * settings = initiator_->getSessionSettings(sessionId);
		if(settings->has("MyPassword"))
		{
			message.setField(FIX::RawData(settings->getString("MyPassword")));
		}
		else
		{
			std::cout << "Warning: MyPassword not found in cfg file for session " << sessionId << std::endl;
		}
	}
}


void Application::toApp( FIX::Message& message, const FIX::SessionID& sessionId)
throw( FIX::DoNotSend )
{
	try
	{
		FIX::PossDupFlag possDupFlag;
		message.getHeader().getField( possDupFlag );
		if ( possDupFlag ) throw FIX::DoNotSend();
	}
	catch ( FIX::FieldNotFound& ) {}

	std::cout << std::endl
	<< "OUT: " << message << std::endl;
}





