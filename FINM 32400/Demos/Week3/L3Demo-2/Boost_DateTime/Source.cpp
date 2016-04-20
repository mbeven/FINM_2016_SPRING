#include <boost/date_time/gregorian/gregorian.hpp>
#include <iostream>
#include <string>

int main()
{
	using namespace boost::gregorian;

	try 
	{
		std::string s("2016-04-12"); 
		date today(from_simple_string(s));
		std::cout << "today: " << today << std::endl;
		
		date_duration d(1);

		date tomorrow = today + d;

		std::cout << "tomorrow: " << tomorrow << std::endl;

		date_duration d2(7);
		date  next_class = today + d2;

		std::cout << "next class: " << next_class << std::endl;

		std::cout << "duration: " << next_class - today << std::endl;

	}
	catch (std::exception& e) 
	{
		std::cout << "  Exception: " << e.what() << std::endl;
	}


	return 0;
}

