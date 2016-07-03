#include <ppltasks.h>
#include <iostream>
#include <array>
#include <numeric>
#include <string>
#include <ppl.h>

//source https://msdn.microsoft.com/en-us/library/dd492427.aspx


void create_task_test()
{
	using namespace concurrency;
	using namespace std;

	auto t = create_task([]()
	{
		cout << "task running ..." << endl;
	});

	t.wait();
}


void continuation_test()
{
	using namespace concurrency;
	using namespace std;

	auto t = create_task([]() -> int
	{
		return 4;
	}).then([](int val) -> int
	{
		return val*val;
	}).then([](int val)
	{
		cout << val << endl;
	}).wait();

}

void continuation_when_all_test()
{
	using namespace concurrency;
	using namespace std;

	array<task<int>, 3> tasks =
	{
		create_task([]() -> int { return 111; }),
		create_task([]() -> int { return 222; }),
		create_task([]() -> int { return 333; })
	};

	//The when_all function produces a task that completes after a set of tasks complete.
	//using when_all to perform an action after a set of tasks finishes. 
	auto joinTask = when_all(begin(tasks), end(tasks)).then([](vector<int> results)
	{
		cout << "The sum is "
			<< accumulate(begin(results), end(results), 0) 
			<< endl;
	});

	// Wait for the tasks to finish.
	joinTask.wait();

}

void continuation_when_any_test()
{
	using namespace concurrency;
	using namespace std;

	// Start multiple tasks.
	array<task<int>, 3> tasks = {
		create_task([]() -> int { return 88; }),
		create_task([]() -> int { return 42; }),
		create_task([]() -> int { return 99; })
	};

	// Select the first to finish.
	when_any(begin(tasks), end(tasks)).then([](pair<int, size_t> result)
	{
		cout << "First task to finish returns "
			<< result.first
			<< " and has index "
			<< result.second
			<< '.' << endl;
	}).wait();

}

void task_group_test()
{
	using namespace concurrency;
	using namespace std;

	concurrency::task_group tg;

	tg.run([]() { cout << "parallel task 1" << endl; });
	tg.run([]() { cout << "parallel task 2" << endl; });
	tg.wait();
}

void parallel_invoke_test()
{
	using namespace concurrency;
	using namespace std;

	concurrency::parallel_invoke(
		[]() { cout << "parallel task 1" << endl; },
		[]() { cout << "parallel task 2" << endl; },
		[]() { cout << "parallel task 3" << endl; },
		[]() { cout << "parallel task 4" << endl; },
		[]() { cout << "parallel task 5" << endl; },
		[]() { cout << "parallel task 6" << endl; },
		[]() { cout << "parallel task 7" << endl; },
		[]() { cout << "parallel task 8" << endl; },
		[]() { cout << "parallel task 9" << endl; },
		[]() { cout << "parallel task 10" << endl; }
	);
}


int main()
{
	using namespace std;

	//cout << "create_task_test" << endl;
	//create_task_test();

	//cout << "\ncontinuation_test" << endl;
	//continuation_test();

	//cout << "\ncontinuation_when_all_test " << endl;
	//continuation_when_all_test();

	//cout << "\ncontinuation_when_any_test " << endl;
	//continuation_when_any_test();
	
	//cout << "\ntask_group test" << endl;
	//task_group_test();

	//cout << "\nparallel_invoke test" << endl;
	//parallel_invoke_test();
}