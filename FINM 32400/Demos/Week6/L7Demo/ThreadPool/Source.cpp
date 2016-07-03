#include <iostream>
#include <vector>
#include <chrono>
#include <future>

#include "TheadPool.h"

int main()
{
	ThreadPool pool(13);

	std::vector<std::future<int>> results;

	for (int i = 0; i < 10; ++i)
	{
		results.push_back(pool.enqueue([i]
		{
			std::this_thread::sleep_for(std::chrono::seconds(100));

			return i*i;
		}));
	}

	for (size_t i = 0; i < results.size(); ++i)
	{
		std::cout << results[i].get() << ' ';
	}

	std::cout << std::endl;

	return 0;
}