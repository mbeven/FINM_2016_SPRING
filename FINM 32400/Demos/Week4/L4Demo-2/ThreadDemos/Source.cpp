#include <iostream>      
#include <future>         

using std::cout;
using std::endl;
using std::vector;
using std::thread;

//////////////
//Future Demo
//source: http://www.cplusplus.com/reference/future/async/
//////////////

bool IsPrime(int number)
{
	cout << "Calculating. Please, wait" << endl;
	for (int i = 2; i < number; ++i)
	{
		//std::this_thread::sleep_for(std::chrono::microseconds(100));
		if (number % i == 0) return false;
	}
	return true;
}

void future_demo()
{
	//call IsPrime(313222313) asynchronously:
	std::future<bool> fut = std::async(IsPrime, 313222313);

	cout << "Checking whether 313222313 is prime.." << endl;
	
	cout << "doing other stuff.... " << endl;

	bool ret = fut.get();     

	if (ret) cout << "It is prime!" << endl;
	else cout << "It is not prime" << endl;
}


//////////////
//Counter Demo
//////////////

int counter_demo()
{
	unsigned long count = 0;

	int numThreads = 2;
	vector<thread> threads(numThreads);

	for (int j = 0; j < numThreads; ++j)
	{
		threads[j] = thread([&count]()
		{
			for (int i = 0; i<100000; ++i)
			{
				count++;
			}
		});
	}

	for (auto& t : threads) t.join();

	return count;
}

int locking_demo()
{
	unsigned long count = 0;
	std::mutex count_mutex; //mutual exclusion



	int numThreads = 8;
	vector<thread> threads(numThreads);

	for (int j = 0; j < numThreads; ++j)
	{
		threads[j] = thread([&]()
		{
			for (int i = 0; i<100000; ++i)
			{
				count_mutex.lock(); // thread gets lock
				count++;
				// always use lock guard.  don't use locks directly
				count_mutex.unlock(); // unlock.  if not unlocked we will get a deadlock
			}
		});
	}

	for (auto iter = threads.begin(); iter != threads.end(); ++iter)
	{
		(*iter).join();
	}

	return count;
}

int locking_raii_demo()
{
	unsigned long count = 0;
	std::mutex count_mutex;

	int numThreads = 8;
	vector<thread> threads(numThreads);

	for (int j = 0; j < numThreads; ++j)
	{
		threads[j] = thread([&]()
		{
			for (int i = 0; i<100000; ++i)
			{
				std::lock_guard<std::mutex> lock(count_mutex);
				count++;
			}
		});
	}

	for (auto iter = threads.begin(); iter != threads.end(); ++iter)
	{
		(*iter).join();
	}

	return count;
}



int main()
{
	//future_demo();
	//cout << counter_demo() << endl;
	cout << locking_demo() << endl;

}