//Thanks to Mike Gatney (Connamara Systems) for QF tips and documentation 

#include "Application.h"

#include <quickfix/Session.h>

#include <iostream>
#include <sstream>
#include <fstream>

using std::endl;
using std::cout;
using std::ifstream;
using std::ofstream;
using std::string;

Application::Application(string& configFile)
	: configFile_(configFile)
{	
	mySenderCompId_ = "Your SenderCompId";
	IdHelper::ReadOrderIdFromFile();
}

Application::~Application()
{
	IdHelper::WriteOrderIdToFile();

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
	
	// Logging on
	for(int i = 0; i < 3; ++i)
	{
		FIX::Session * orderSession = FIX::Session::lookupSession(orderSessionId_);
		if(orderSession)
		{
			if(orderSession->isLoggedOn())
			{
				return;
			}
		}
		cout << "[init] Waiting for all FIX Sessions to logon..." << endl;
		FIX::process_sleep(2);
	}

	throw std::runtime_error("[init] Fatal error: timed out waiting for FIX Session to logon!");
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
			case '1':
				sendMarketOrder();
				break;
			case '2':
				sendLimitOrder();
				break;
			case '3':
				sendCancelOrder();
				break;
			case '4':
				sendCancelReplaceOrder();
				break;
			case '5':
				keepRunning = false;
				break;
			}
		}
		catch (std::exception & e)
		{
			cout << "Message Not Sent: " << e.what() << endl;
		}
	}
}

char Application::queryAction()
{
	cout << endl
		<< "1) Enter Market Order" << endl
		<< "2) Enter Limit Order" << endl
		<< "3) Cancel Order" << endl
		<< "4) Replace Order" << endl
		<< "5) Quit" << endl;

	cout << "Enter Action: ";
	
	char value;
	std::cin >> value;

	return value;
}

//TT API:
//https://www.tradingtechnologies.com/help/fix-adapter-reference/whats-new-in-fix-adapter-717x/

//https://www.tradingtechnologies.com/help/fix-adapter-reference/new-order---single-d/
void Application::sendMarketOrder()
{
	FIX42::NewOrderSingle newOrder;

	newOrder.setField(FIX::ClOrdID(IdHelper::GetNextOrderId()));
	//newOrder.setField(FIX::HandlInst('1'));
	newOrder.setField(FIX::TransactTime());

	//component block: instrument
	newOrder.setField(FIX::SecurityExchange("CME"));
	newOrder.setField(FIX::Symbol("ES"));
	newOrder.setField(FIX::SecurityType("FUT"));
	newOrder.setField(FIX::MaturityMonthYear("201606"));

	//component block: trader
	newOrder.setField(FIX::Account(mySenderCompId_)); 
	newOrder.setField(FIX::Rule80A('A'));
	newOrder.setField(FIX::CustomerOrFirm(0));

	newOrder.setField(FIX::OrderQty(1));
	newOrder.setField(FIX::Side(FIX::Side_BUY));
	newOrder.setField(FIX::OrdType(FIX::OrdType_MARKET));
	newOrder.setField(FIX::TimeInForce(FIX::TimeInForce_DAY)); //this is default value

	FIX::Session::sendToTarget(newOrder, orderSessionId_);
}

void Application::sendLimitOrder()
{
	cout << "Sending Limit Order" << endl;

	FIX42::NewOrderSingle newOrder;

	newOrder.setField(FIX::ClOrdID(IdHelper::GetNextOrderId()));
	//newOrder.setField(FIX::HandlInst('1'));
	newOrder.setField(FIX::Symbol("ES"));
	newOrder.setField(FIX::Side(FIX::Side_BUY));
	newOrder.setField(FIX::TransactTime());
	newOrder.setField(FIX::OrdType(FIX::OrdType_LIMIT));
	newOrder.setField(FIX::Price(200550));
	newOrder.setField(FIX::OrderQty(1));
	newOrder.setField(FIX::TimeInForce(FIX::TimeInForce_DAY));
	newOrder.setField(FIX::SecurityExchange("CME"));
	newOrder.setField(FIX::SecurityType("FUT"));
	newOrder.setField(FIX::MaturityMonthYear("201606"));
	newOrder.setField(FIX::Account(mySenderCompId_));   
	newOrder.setField(FIX::CustomerOrFirm(0));
	newOrder.setField(FIX::Rule80A('A'));

	FIX::Session::sendToTarget(newOrder, orderSessionId_);
}

void Application::sendCancelOrder()
{
	cout << "Sending Cancel Order" << endl;

	
	FIX42::OrderCancelRequest cancelOrder;
	cancelOrder.setField(FIX::OrigClOrdID(IdHelper::GetCurrentOrderId()));
	cancelOrder.setField(FIX::ClOrdID(IdHelper::GetNextOrderId()));
	

	FIX::Session::sendToTarget(cancelOrder, orderSessionId_);
}

void Application::sendCancelReplaceOrder()
{
	cout << "Sending Cancel Replace Order" << endl;

	FIX42::OrderCancelReplaceRequest cancelReplace;

	//incomplete
	
}


//https://www.tradingtechnologies.com/help/fix-adapter-reference/execution-report-8/

void Application::onMessage(const FIX42::ExecutionReport& msg, const FIX::SessionID&)
{
	FIX::ExecType execType;
	FIX::Symbol symbol;
	FIX::MaturityMonthYear maturityMonthYear;
	FIX::Side side;

	// See what kind of execution report this is:
	msg.get(execType);

	if (FIX::ExecType_FILL == execType.getValue() 
		|| FIX::ExecType_PARTIAL_FILL == execType.getValue())
	{
		FIX::LastShares lastQty;
		FIX::LastPx lastPx;
		msg.get(symbol);
		msg.get(maturityMonthYear);
		msg.get(side);
		msg.get(lastQty);
		msg.get(lastPx);

		if (FIX::Side_BUY == side)
		{
			cout << "Bought, Qty: " << lastQty.getValue()
				<< " Price: " << lastPx.getValue();
		}
		else if (FIX::Side_SELL == side)
		{
			cout << "Sold, Qty: " << lastQty.getValue()
				<< " Price: " << lastPx.getValue();
		}
	}
	else if (FIX::ExecType_REJECTED == execType.getValue())
	{
		FIX::OrderQty orderQty;
		msg.get(symbol);
		msg.get(maturityMonthYear);
		msg.get(side);
		msg.get(orderQty);

		if (FIX::Side_BUY == side)
		{
			cout << "Buy Order Rejected, Qty: " << orderQty.getValue() << endl;
		}
		else if (FIX::Side_SELL == side)
		{
			cout << "Sell Order Rejected, Qty: " << orderQty.getValue() << endl;
		}
	}
	else if (FIX::ExecType_NEW == execType.getValue())
	{
		// Our order was accepted (but has not yet been filled)
		cout << "New Order Received: " << symbol << endl;
	}
	else if (FIX::ExecType_CANCELED == execType.getValue())
	{
		cout <<  "Order Canceled: " << symbol << endl;
	}
	else
	{
		cout << "Not sure what to do with ExecutionReport with ExecType = " << 
			execType << ": " << msg << endl;
	}
}

//-----------------------------------------------------------------------------
// Called by QF when an App-type message is received from the counterparty.
//
// Examples of Application-type messages are ExecutionReport and CancelReject.
// We could just write all of our code for handling these message right here in
// this callback.
//
// However, we would probably end up with a really, really long function if we
// did that.  Instead, we usually just call the QF crack() function here, which
// calls the proper onMessage() callback for whatever MsgType we just received.
void Application::fromApp(const FIX::Message& message, const FIX::SessionID& sessionID)
throw(FIX::FieldNotFound, FIX::IncorrectDataFormat,
FIX::IncorrectTagValue, FIX::UnsupportedMessageType)
{
	cout << endl << "IN: " << message << endl;
	crack(message, sessionID);
}

//-----------------------------------------------------------------------------
// Called by QF after we call Session::sendToTarget() to send a message, right
// before the message is actually transmitted.  
//
// Examples of App-type messages that we might send are NewOrderSingle,
// OrderCancelRequest, and MarketDataRequest.
//
// The FIX Protocol guarantees in-order delivery of all messages.  For example,
// if you temporarily lose your network connection, FIX Protocol ensures that
// any messages that failed to make it to either counterparty will be
// re-transmitted.
//
// This is helpful behaviour when you are, say, receiving an ExecutionReport.  It
// is probably NOT helpful behaviour if say, you send a NewOrderSingle which gets
// re-transmitted an hour later when the network suddenly comes back up and the
// market has moved significantly!
//
// This is your chance to thwart the automatic resend behaviour if you do not
// want it.
void Application::toApp(FIX::Message& message, const FIX::SessionID& sessionID) throw(FIX::DoNotSend)
{
	try
	{
		FIX::PossDupFlag possDupFlag;
		message.getHeader().getField(possDupFlag);
		if (possDupFlag) throw FIX::DoNotSend();
	}
	catch (FIX::FieldNotFound&) {}

	cout << endl
		<< "OUT: " << message << endl;
}


//-----------------------------------------------------------------------------
// Called by QF when a Session is created (but before it is logged on).
// We do not usually do anything here.
void Application::onCreate( const FIX::SessionID& sessionId)
{
}

//-----------------------------------------------------------------------------
// Called by QF whenever a Session is successfully logged on.
//
// We need to know which SessionID to use when sending orders vs sending a
// market data subscription.  The onLogon() callback is a good time to
// distinguish between the two Sessions.  We will use a couple of custom config
// file options to help us do that.
void Application::onLogon( const FIX::SessionID& sessionId )
{
	
	// Ask QF for the SessionSettings for this Session
	const FIX::Dictionary* settings = initiator_->getSessionSettings(sessionId);

	// Grab our custom "MyOrderSession" parameter (if it exists) from the SessionSettings
	if(settings->has("MyOrderSession") && settings->getBool("MyOrderSession"))
	{
		orderSessionId_ = sessionId;

		cout << "[onLogon] " << orderSessionId_ << " (MyOrderSession)" << endl;
	}
}

//-----------------------------------------------------------------------------
// Called by QF whenever a Session is successfully logged out.
//
void Application::onLogout( const FIX::SessionID& sessionID )
{
	cout << "Logout - " << sessionID << endl;
}


//-----------------------------------------------------------------------------
// Called by QF when an Admin-type message is received from the counterparty.
//
// Examples of Admin-type messages are Logon, Logout, and Heartbeat.
//
// We almost never want or need to do anything in this callback.  QF handles
// these types of messages for us automatically.
void Application::fromAdmin( const FIX::Message&, const FIX::SessionID& ) 
	throw( FIX::FieldNotFound, FIX::IncorrectDataFormat, FIX::IncorrectTagValue, FIX::RejectLogon )
{}


//-----------------------------------------------------------------------------
// Called by QF right before an Admin-type message is sent to the counterparty.
//
// Examples of Admin-type messages are Logon, Logout, and Heartbeat.  We never
// send these types of messages ourselves -- QF does so for us automatically.
//
// However, we may need to customize the content of an Admin-type -- e.g., our
// counterparty may require us to specify a username or password.
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
			cout << "Warning: MyPassword not found in cfg file for session " << sessionId << endl;
		}
	}
}
