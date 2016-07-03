#include "Application.h"
#include "MyStrategy.h"

#include <string>
#include <iostream>
#include <memory>
 
int main(int argc, char* argv[])
{
	try
	{
	
		const std::string cfgFileName = "../config/tt.cfg";
		const std::string symbol = "xx";
		const std::string maturityMonthYear = "xx";
		const std::string account = "uchidts10";

		// create our strategy and connect it to our Application FIX interface
		MyStrategy strategy(symbol, maturityMonthYear, account);
		Application Application(strategy);
		Application.Init(cfgFileName);
		
		// quickfix is now running in the background, so we just wait here until the user hits ENTER to shut us down
		std::cout << std::endl << "Hit [ENTER] to quit..." << std::endl;
		std::string input;
		std::getline(std::cin, input);
	}
	catch(const std::exception & e)
	{
		std::cerr << std::endl << e.what() << std::endl;
		return 1;
	}
	return 0;
}

