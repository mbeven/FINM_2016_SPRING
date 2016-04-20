#include <thread>
#include <mutex>
#include <iostream>
#include <vector>
#include <chrono>

using std::cout;
using std::endl;
using std::vector;
using std::thread;

using namespace std::chrono;

long counterA = 0;
long counterB = 0;

/*
std::mutex counterA_mutex;
std::mutex counterB_mutex;
*/

std::mutex counter_mutex;



void IncrementA()
{
	std::lock_guard<std::mutex> lock(counter_mutex);

	//std::lock_guard<std::mutex> lockA(counterA_mutex); 
	for (int i = 0; i < 1000000; i++)
	{
		for (int j = 0; j < 1000000; ++j)
		{
			counterA++;
		}
	}
}


void IncrementB()
{	
	std::lock_guard<std::mutex> lock(counter_mutex);

	//std::lock_guard<std::mutex> lockB(counterB_mutex);
	for (int i=0; i<1000000; i++) 
	{
		counterB ++;
	}
	
}

void IncrementA_B()
{
	std::lock_guard<std::mutex> lock(counter_mutex);

	//std::lock_guard<std::mutex> lockA(counterA_mutex);
	for (int i = 0; i < 1000000; i++)
	{
		for (int j = 0; j < 1000000; ++j)
		{
			counterA++;
		}
	}


	//std::lock_guard<std::mutex> lockB(counterB_mutex);
	for (int i = 0; i < 1000000; i++)
	{
		for (int j = 0; j < 1000000; ++j)
		{
			counterB++;
		}
	}

}

int main()
{
	try
	{	
		auto start = high_resolution_clock::now();
		thread t1(IncrementA_B);
		thread t2(IncrementA);

		t1.join();
		t2.join();

		auto end = high_resolution_clock::now();

		std::cout << "time : " << duration_cast<milliseconds>(end - start).count() << endl;
	}
	catch(std::exception& e)
	{
		cout << e.what() << endl;
	}
}	

	
