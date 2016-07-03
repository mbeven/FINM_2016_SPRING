#include <iostream>
#include <thread>
#include <string>
#include <algorithm>
#include <future>

using std::cout;
using std::endl;
using std::thread;
using std::string;
using std::future;

void DisplayGreeting()
{
	std::cout << "Hello World" << std::endl;
}

// returning a result at the end of a task
int GetValueOut(int& val)
{
	val = 10;
}

int main()
{
	//DisplayGreeting();

	std::thread t(DisplayGreeting);
	t.join(); // calling main thread stops until t1 is done
}



