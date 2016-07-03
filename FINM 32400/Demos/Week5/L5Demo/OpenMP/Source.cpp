#include <omp.h>
#include <Windows.h>
#include <iostream>
#include <array>

using std::cout;
using std::endl;
using std::flush;


//illustrates parallel directive
void hello_world_test()
{
	#pragma omp parallel num_threads(5) // pragma means commands to the compiler.  this is an omp command
	cout << "Hello, world " <<  endl;
}

void serial_parallel_serial_test()
{
	//do some serial work
	cout << "Serial region #threads:" << omp_get_num_threads() << endl;
	
	//do some work in parallel
	{
		#pragma omp parallel num_threads(4) 

		cout << "Parallel Region: #threads:" << omp_get_num_threads() << endl;
	}

	//do some work work in serial
	cout << "Serial Region: #threads" << omp_get_num_threads() << endl;

}

void parallel_for_test()
{
	#pragma omp parallel for
	for (int i = 0; i < 4; ++i)
	{
		cout << "thread #: " << omp_get_thread_num() << endl;
	}
}

//illustrates master
void master_thread_test()
{
#pragma omp parallel 
	cout << "Hello, world" << endl;

#pragma omp master // runs in just one thread.  will run the other threads separately
	cout << "Hello, class" << endl;
}

//illustrates barrier
void barrier_test()
{
	#pragma omp parallel num_threads(4)
	cout << "Hello, world" << endl; // do something

	#pragma omp barrier // wait for result

	#pragma omp parallel
	cout << "Hello, class" << endl; // do something else
}

//illustrates critical
void critical_test()
{
	#pragma omp parallel for
	for (int i = 0; i < 16; ++i)
	{
		#pragma omp critical(log) // creates orderly output - global lock
		cout << "(" << omp_get_thread_num() << ":" << i << ")" << flush;
	}

	cout << endl;
}

void Task1()
{
	unsigned long res = 0;
	for (int i = 0; i < 1000; ++i)
	{
		res += i;
	}
	cout << "Task 1 complete: " << res << endl;
}

void Task2()
{
	unsigned long res = 0;
	for (int i = 0; i < 1000; ++i)
	{
		res += i*i;
	}
	cout << "Task 2 complete: " << res << endl;
}

void sections_test()
{
	#pragma omp parallel
	{
		#pragma omp sections
		{
			#pragma omp section
			Task1();

			#pragma omp section
			Task2();
		}
	}
}


void static_scheduling_test()
{
	double start = omp_get_wtime();

	#pragma omp parallel for schedule(static) num_threads(4)
	for (int i = 0; i<16; ++i)
	{
		#pragma omp critical(log)
		cout << "(" << omp_get_thread_num() << ":" << i << ")" << flush;
		if (i<2)
		{
			Sleep(2000);  // simulate long work
		}
		else
		{
			Sleep(100);  // simulate short work
		}
	}

	double end = omp_get_wtime();

	cout << "Static Thread Scheduling: Time elapsed: " << (end - start) << endl;
}

void dynamic_scheduling_test()
{
	double start = omp_get_wtime();
	#pragma omp parallel for schedule(dynamic) num_threads(4)

	for (int i = 0; i<16; ++i)
	{
		#pragma omp critical(log)

		cout << "(" << omp_get_thread_num() << ":" << i << ")" << flush;
		if (i<2)
		{
			Sleep(2000);  // simulate long work
		}
		else
		{
			Sleep(100);  // simulate short work
		}
	}

	double end = omp_get_wtime();

	cout << "Dynamic Thread Scheduling: Time elapsed: " << (end - start) << endl;
}

int main()
{
	//cout << "Running Hello World Test:" << endl;
	//hello_world_test();

	//cout << "Running Serial -> Parallel -> Serial Test:" << endl;
	//serial_parallel_serial_test();

	//cout << "Running Parallel For Test" << endl;
	//parallel_for_test();

	//cout << "Running Master Thread Test" << endl;
	//master_thread_test();

	//cout << "Running Barrier Test" << endl;
	//barrier_test();

	//cout << "Running Critical Test" << endl;
	//critical_test();

	//cout << "Running Sections Test" << endl;
	//sections_test();

	//cout << "Running Static Scheduling Test" << endl;
	//static_scheduling_test();

	//cout << "Running Dynamic Scheduling Test" << endl;
	//dynamic_scheduling_test();

}