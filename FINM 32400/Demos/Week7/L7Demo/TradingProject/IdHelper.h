#ifndef ID_HELPER_H
#define ID_HELPER_H

#include <string>

using std::string;

/// Creates unique IDs for orders and market data subscriptions
class IdHelper
{
public:

	static string GetNextOrderId();

	static string GetCurrentOrderId();
	
	static string GetNextMDRequestId();
	
	static void WriteOrderIdToFile();
	
	static void ReadOrderIdFromFile();

private:
	IdHelper();
	IdHelper(const IdHelper&) = delete;
	IdHelper& operator=(const IdHelper&) = delete;

private:
	static int orderId_;
	static int mdRequestId_;
};

#endif