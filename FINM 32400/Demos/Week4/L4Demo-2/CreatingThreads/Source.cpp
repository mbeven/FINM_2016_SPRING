#include <iostream>
#include <thread>
#include <string>
#include <algorithm>


using std::cout;
using std::endl;
using std::thread;
using std::string;

void DisplayGreeting1()
{
	cout << "Hello, World" << endl;

}

void DisplayGreeting2(string& msg)
{
	cout << msg << endl;
}


class ThreadTask
{
public:
	void operator()() const
	{
		cout << "Hello, World" << endl;
	}
};


int main()
{
	//using a free function
	string msg = "hello, class";
	thread t1(DisplayGreeting2, std::ref(msg));
	t1.join();

	cout << msg << endl;


	
	//using a lambda
	std::thread t2([]
	{
		cout << "Hello, World" << endl;
	});

	t2.join();
	

	//using  a function object
	ThreadTask task;
	thread t3(task);

	t3.join();
	
}



