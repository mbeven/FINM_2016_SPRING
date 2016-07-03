#include <iostream>
#include <vector>
#include <cmath>
#include <math.h>
#include <numeric>
#include <algorithm> // used sorting for parts (c) to (e)
using std::cout;
using std::endl;
using std::vector;
using std::copy_if; // used for part (f)
using std::find;
using std::for_each; // used in part (g)
using std::accumulate; // used in part (g)

vector<int> v{5,4,3,2,1,0,1,2,3,4,5};

// i didn't use this given format for the questions.  my answers are placed in the main() file.  

// this function is used for part (f)
bool Greater3(int number)
{
	if (number > 3) return true;
	else return false;
}

// this function is used for part (g)
void cube(int elem)
{
	int sum = 0;
	int cubed = elem*elem*elem;
	sum = sum + cubed;
	
	cout << sum << endl;
}

int main()
{
	///////////////////////////////////////////////////////////////////////////
	//part (a)
	cout << "Part (a) " << endl;
	vector<int>::iterator iter;
	for (iter = v.begin(); iter != v.end(); ++iter)
	{
		cout << *iter << endl;
	}
	///////////////////////////////////////////////////////////////////////////

	///////////////////////////////////////////////////////////////////////////
	//part (b)
	cout << "Part (b) " << endl;
	// sort based on the range
	vector<int>::reverse_iterator r_iter;
	for (auto r_iter = v.rbegin(); r_iter != v.rend(); ++r_iter)
	{
		cout << *r_iter << endl;
	}
	///////////////////////////////////////////////////////////////////////////

	//for parts (c) to (e), sort the values to find max min and median
	sort(v.begin(), v.end());
	int N = v.size(); // get size of vector

	///////////////////////////////////////////////////////////////////////////
	//part (c)
	cout << "Part (c) " << endl;
	cout << v[N-1] << endl; // last value of the sorted array is the maximum
	///////////////////////////////////////////////////////////////////////////

	///////////////////////////////////////////////////////////////////////////
	//part (d)
	cout << "Part (d) " << endl;
	cout << v[0] << endl; // first value of the sorted array is the minimum
	///////////////////////////////////////////////////////////////////////////

	///////////////////////////////////////////////////////////////////////////
	//part (e)
	cout << "Part (e) " << endl;
	cout << v[(N-1)/2] << endl; // middle value of the sorted array is the median
	///////////////////////////////////////////////////////////////////////////

	///////////////////////////////////////////////////////////////////////////
	//part (f)
	cout << "Part (f) " << endl;
	vector<int> unique;
	for (int i = 0; i < N; i++)
	{
		if (v[i] > 3) // if the value in the vector is greater than 3, look into another 'unique' vector to see if it's already there
		{
			int M = unique.size();
			if (M == 0) // there's nothing in the unique vector yet
			{
				unique.push_back(v[i]);
			}
			else
			{
				for (int j = 0; j < M; j++) // for the size of the unique vector
				{
					if (v[i] == unique[j])
					{
						break; // break because it already exists
					}
					else if (j == M) // if we reach the end and code hasn't broken
					{
						unique.push_back(v[i]); // add it to the unique vector
					}
				}
			}
		}
	}
	vector<int>::iterator uiter; // create new iterator
	for (uiter = unique.begin(); uiter != unique.end(); ++uiter)
	{
		cout << *uiter << endl; // output
	}

	///////////////////////////////////////////////////////////////////////////

	///////////////////////////////////////////////////////////////////////////
	//part (g)
	cout << "Part (g) " << endl;
	//for_each(v.begin(), v.end(), cube);
	int sum = 0;
	for (int i = 0; i < N; i++) // N is found above using v.size()
	{
		sum = sum + v[i] * v[i] * v[i];
	}
	cout << sum << endl;

	///////////////////////////////////////////////////////////////////////////

	///////////////////////////////////////////////////////////////////////////
	//part (h)
	cout << "Part (h) " << endl;
	int sum2 = 0;
	for (int i = 0; i < N; i++) // N is found above using v.size()
	{
		sum2 = sum2 + v[i];
	}
	cout << "Mean: " << sum2/N << endl;

	int sum3 = 0;
	for (int i = 0; i < N; i++) // N is found above using v.size()
	{
		sum3 = sum3 + (v[i] - sum2/2)* (v[i] - sum2 / 2);
	}

	cout << "Variance: " << sum3 / (N - 1) << endl;
	///////////////////////////////////////////////////////////////////////////

	///////////////////////////////////////////////////////////////////////////
	//part (i)
	cout << "Part (i) " << endl;
	/*for (iter = v.begin(); iter != v.end(); ++iter)
	{
		int sum = 0;
		if (sum == 0 && *iter == 4)
		{
			replace(v.begin(), v.end(), //range
				4, // old value
				44); // new value)
			sum = sum + 1;
		}

		cout << *iter << endl;
	}*/

	vector<int> v{ 5,4,3,2,1,0,1,2,3,4,5 }; // reset vector v so we can do this part
	int sum4 = 0; 
	for (int i = 0; i < N; i++) // N is found above using v.size()
	{
		if (sum4 == 0 && v[i] == 4)
		{
			v[i] = 44;
			sum4 = sum4 + 1;
		}
	}
	for (iter = v.begin(); iter != v.end(); ++iter)
	{
		cout << *iter << endl;
	}
	///////////////////////////////////////////////////////////////////////////


}