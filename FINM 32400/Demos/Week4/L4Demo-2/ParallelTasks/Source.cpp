#include <chrono>
#include <iostream>
#include <thread>
#include <vector>

using namespace std::chrono;

using std::cout;
using std::endl;
using std::thread;
using std::vector;

//Show the number of distinct pairs (i, j) such that values[i] + values[j]  == M 
//Source: Robert Sedgewick, Kevin Wayne. Algorithms (4th Edition).
void Count2Sum(const vector<int>& values, int M)
{	
	int count = 0;
	int N = values.size();
	for (int i = 0; i < N; i++)
	{
		for (int j = i + 1; j < N; j++)
		{
			if (values[i] + values[j] == M)
			{
				count++;
			}
		}
	}

	//cout << "Count2Sum, " << M << ":" << count << endl;
}

void test0()
{
	vector<int> values;
	int N = 5000;

	for (int i = 0; i<N; ++i)
	{
		int v = rand() % 100;         // v in the range 0 to 99

		values.push_back(v);
	}

	auto start1 = high_resolution_clock::now();

	Count2Sum(values, 100);
	
	auto end1 = high_resolution_clock::now();

	cout << "Time elapsed :" << duration_cast<milliseconds>(end1 - start1).count() << " ms " << endl;
}

void test1()
{
	vector<int> values;
	int N = 5000;

	for (int i = 0; i<N; ++i)
	{
		int v = rand() % 100;         // v in the range 0 to 99

		values.push_back(v);
	}

	auto start1 = high_resolution_clock::now();

	Count2Sum(values, 100);

	Count2Sum(values, 105);

	auto end1 = high_resolution_clock::now();

	cout << "(Serial) Time elapsed :" << duration_cast<milliseconds>(end1 - start1).count() << " ms " << endl;

	std::this_thread::sleep_for(std::chrono::microseconds(3000));

	auto start2 = high_resolution_clock::now();

	thread t1(Count2Sum, std::ref(values), 100);

	thread t2(Count2Sum, std::ref(values), 105);

	t1.join();

	t2.join();

	auto end2 = high_resolution_clock::now();

	cout << "(Parallel) Time elapsed :" << duration_cast<milliseconds>(end2 - start2).count() << " ms " << endl;

}

void test2()
{
	vector<int> values;
	int numVals = 5000;

	for (int i = 0; i<numVals; ++i)
	{
		int v = rand() % 100;         // v in the range 0 to 99

		values.push_back(v);
	}

	int N = std::thread::hardware_concurrency();

	cout << "Hardware Concurrency: " << N << endl;
	
	for (int n = N-4; n <= N+2; ++n)
	{
		std::this_thread::sleep_for(std::chrono::seconds(2));
	
		auto start = high_resolution_clock::now();

		std::vector<std::thread> tasks;
		tasks.reserve(n);

		for (int i = 0; i < n; ++i)
		{
			tasks.emplace_back(thread(Count2Sum, std::ref(values), 100 + i));
		}

		for (int i = 0; i < n; ++i)
		{
			tasks[i].join();
		}

		auto end = high_resolution_clock::now();
		cout << n << " (Parallel) Time elapsed :" << "  " << duration_cast<milliseconds>(end - start).count() << " ms " << endl;
	}
}

int main()
{
	test0();
}

