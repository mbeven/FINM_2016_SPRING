#include <iostream>
#include <iomanip>
#include <chrono>
#include <algorithm>
#include <numeric>
#include <array>
#include <vector>
#include <Eigen/Dense>

#include <concurrent_vector.h>
#include <concurrent_unordered_map.h>
#include <ppl.h>
#include <Windows.h>
#include <unordered_map>
#include <mutex>

using std::cout;
using std::endl;
using namespace std::chrono;

//source: most examples were taken from msdn.com 
//some examples are changed slightly to illustrate various points 

void ConcurrentVector_test()
{
	using namespace concurrency;

	concurrent_vector<int> v; //defined in:concurrent_vector.h
	//std::vector<int> v; // store some integers in a function
	//std::mutex m;
	
	// Perform four tasks in parallel. 
	parallel_invoke( //parallel_invoke to create two tasks
		[&v]//, &m] // pass a lambda
	{
		for (int i = 0; i < 10000; ++i) // create a task
		{
			std::lock_guard<std::_Mutex_base> guard(m);
			v.push_back(i); // store values in vector
		}
	},
		[&v]//, &m]
	{
		for (int i = 0; i < 10000; ++i) // create another task
		{
			std::lock_guard<std::_Mutex_base> guard(m);
			v.push_back(3 * i); //adding values to vector
		}
	});
}
//NOTE: modifying the same vector is not a good idea - raised conditions.  Use mutex lock to fix

//Source: Msdn
//defined in concurrent_unordered_map.h
void ConcurrentMap_test()
{
	// Insert a number of items into the map in parallel.
	concurrency::concurrent_unordered_map<char, int> m;
	//std::unordered_map<char, int> m;

	concurrency::parallel_invoke(
		[&m]
	{
		for (int i = 0; i < 10; ++i)
		{
			char key = 'a' + (i % 9); // Geneate a key in the range [a,i]. 
			int value = i;          // Set the value to i.
			m.insert(std::make_pair(key, value));
		}
	},
		[&m]
	{
		for (int i = 0; i < 10; ++i)
		{
			char key = 'a' + (i % 9); // Geneate a key in the range [a,i]. 
			int value = 3 * i;          // Set the value to i.
			m.insert(std::make_pair(key, value));
		}
	});
}

// Determines whether the input value is prime. 
bool is_prime(int n)
{
	if (n < 2)
	{
		return false;
	}
	for (int i = 2; i < n; ++i)
	{
		if ((n % i) == 0)
			return false;
	}
	return true;
}


void IsPrime_test()
{
	using namespace concurrency;

	// Create an array object that contains 200000 integers. 
	std::array<int, 200000> a;

	// Initialize the array such that a[i] == i.
	iota(begin(a), end(a), 0);

	auto start1 = high_resolution_clock::now();

	// Compute the sum of the numbers in the array that are prime.      
	transform(a.begin(), a.end(), a.begin(), [](int i)
	{
		return is_prime(i) ? i : 0;
	});

	long prime_sum1 = accumulate(a.begin(), a.end(), 0);

	auto end1 = high_resolution_clock::now();

	cout << "Prime Sum :" << prime_sum1 << endl;

	cout << "Elapsed (Serial): " << duration_cast<milliseconds>(end1 - start1).count() << " ms" << endl;

	Sleep(100);

	// Initialize the array such that a[i] == i.
	iota(begin(a), end(a), 0);

	auto start2 = high_resolution_clock::now();

	// Now perform the same task in parallel.
	parallel_transform(a.begin(), a.end(), a.begin(), [](int i)
	{
		return is_prime(i) ? i : 0;
	});
	long prime_sum2 = parallel_reduce(a.begin(), a.end(), 0);

	auto end2 = high_resolution_clock::now();

	cout << "Prime Sum :" << prime_sum2 << endl;

	cout << "Elapsed (Parallel): " << duration_cast<milliseconds>(end2 - start2).count() << " ms" << endl;

}

void ParallelFor_test()
{
	using namespace concurrency;

	parallel_for(1, 9, [](int value)
	{
		cout << value << endl;
	});
}


int main()
{
	//Using Concurrent Vector
	//ConcurrentVector_test();

	//Using Concurrent map
	//ConcurrentMap_test();

	//IsPrime_test();

	//ParallelFor_test();


}