#ifndef ID_HELPER_H
#define ID_HELPER_H

#include <string>

using std::string;

// Creates unique IDs for orders and market data subscriptions
class IdHelper
{
public:
	IdHelper();

	~IdHelper();

	static string GetNextOrderId();

	static string GetCurrentOrderId();
	
	static string GetNextMDRequestId();
	
	static void WriteOrderIdToFile();
	
	int ReadOrderIdFromFile();

private:
	IdHelper(const IdHelper&) = delete;
	IdHelper& operator=(const IdHelper&) = delete;

	static int orderId_;
	static int mdRequestId_;
};

#endif