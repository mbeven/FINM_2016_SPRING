#include <Eigen/Dense>

#include <iostream>
#include <iomanip>
#include <thread>
#include <vector>
#include <chrono>

using namespace std::chrono;

using std::thread;
using std::vector;
using std::cout;
using std::endl;
using Eigen::MatrixXd;



void CalculateRow(const MatrixXd& m1, const MatrixXd& m2, MatrixXd& m3, 
	int row, int rows, int columns)
{
	//write code
}

void MatrixMultiplySerial(const MatrixXd& m1, const MatrixXd& m2, MatrixXd& m3,
	int rows, int columns)
{
	for (int i = 0; i < rows; ++i)
	{
		CalculateRow(m1, m2, m3, i, rows, columns);
	}
}


void MatrixMultiplyParallel(const MatrixXd& m1, const MatrixXd& m2, MatrixXd& m3,
	int rows, int columns)
{
	vector<thread> threads(rows);

	for (int i = 0; i < rows; ++i)
	{
		threads[i] = thread([&]()
		{
			CalculateRow(m1, m2, m3, i, rows, columns);
		});
	}

	for (thread& t : threads)
	{
		t.join();
	}
}


void matrix_multiply_demo()
{
	const int rows = 300;
	const int columns = 300;
	MatrixXd m1(rows, columns);

	//populate the matrix
	for (int i=0; i < rows; ++i)
	{
		for (int j=0; j < columns; ++j)
		{ 
			m1(i, j) =  10.0 * std::rand() /RAND_MAX;
		}
	}

	//populate the matrix
	MatrixXd m2(rows, columns);
	for (int i=0; i < rows; ++i)
	{
		for (int j=0; j < columns; ++j)
		{	 
			m2(i, j) =  10.0 * std::rand() /RAND_MAX;
		}
	}

	MatrixXd m3(rows, columns);

	//Matrix multiplication not using threads
	auto start1 = high_resolution_clock::now();

	MatrixMultiplySerial(m1, m2, m3, rows, columns);

	auto end1 = high_resolution_clock::now();

	cout << "(Serial) Time elapsed " << duration_cast<milliseconds>(end1 - start1).count() << "  ms" << endl;
	
	std::this_thread::sleep_for(std::chrono::microseconds(3000));

	//Matrix multiplication using threads
	auto start2 = high_resolution_clock::now();

	MatrixMultiplyParallel(m1, m2, m3, rows, columns);

	auto end2 = high_resolution_clock::now();

	cout << "(Parallel) Time elapsed " << duration_cast<milliseconds>(end2 - start2).count() << " ms" << endl;	
}

int main()
{
	matrix_multiply_demo();
}
