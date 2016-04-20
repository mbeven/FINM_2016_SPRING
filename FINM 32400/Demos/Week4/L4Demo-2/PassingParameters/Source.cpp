#include <iostream>
#include <thread>
#include <string>
#include <algorithm>

using std::cout;
using std::endl;
using std::thread;
using std::string;

void DisplayGreeting(string& msg)
{
	std::reverse(msg.begin(), msg.end());
}

class ThreadTask
{
public:
	void operator()(string msg) const
	{
		cout << msg << endl;
	}
};


int main()
{
	string msg = "Hello, World";
	
	thread t(DisplayGreeting, std::ref(msg));
	t.join();

	cout << msg << endl;

	////using funtions objects
	ThreadTask task;
	string msg("hi, class");
	std::thread t2(task, msg);
	t2.join();

	////using lambda
	auto DisplayGreetingLambda = [](string msg)
	{
		cout << msg << endl;
	};

}