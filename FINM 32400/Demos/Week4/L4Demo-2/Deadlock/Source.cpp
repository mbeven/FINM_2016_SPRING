#include <thread>
#include <mutex>
#include <iostream>
#include <vector>

using std::cout;
using std::endl;
using std::vector;
using std::thread;

std::recursive_mutex count_mutex;

//std::mutex count_mutex;

long counter = 0;

void Increment()
{
	std::lock_guard<std::recursive_mutex> guard(count_mutex);
	//std::lock_guard<std::mutex> guard(count_mutex);
	counter ++;
}

void Decrement()
{
	std::lock_guard<std::recursive_mutex> guard(count_mutex);
	//std::lock_guard<std::mutex> guard(count_mutex);
	counter --;
}

void IncrementAndDecrement()
{
	std::lock_guard<std::recursive_mutex> guard(count_mutex);
	//std::lock_guard<std::mutex> guard(count_mutex);
	Increment();
	Decrement();
}

int main()
{
	try
	{
		Increment();
		Decrement();
		
		IncrementAndDecrement();

		cout << counter << endl;
	}
	catch(std::exception& e)
	{
		cout << "Caught Excepiton " << e.what() << endl;
	}
}	

	
