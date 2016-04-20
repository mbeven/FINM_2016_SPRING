#include "Application.h"

#include <string>
#include <iostream>
#include <memory>

int main()
{
	try
	{
		
		const std::string cfgFileName = "../config/tt.cfg"; 
		
	
		Application Application;
		
		Application.Init(cfgFileName);
		
		Application.Run();

		// quickfix is now running in the background, so we just wait here 
		//..until the user hits ENTER to shut us down
		std::cout << std::endl << "Hit [ENTER] to quit..." << std::endl;
		std::string input;
		std::getline(std::cin, input);
	}
	catch(const std::exception & e)
	{
		std::cerr << std::endl << e.what() << std::endl;
	}
}

