#include <iostream>
#include <string>

using namespace std;

class Singleton
{
public:
	// If control enters the declaration concurrently while
	// the variable is being initialised, the oncurrent exectuion
	// shall wait for completion of the initialisation
	static Singleton& Instance()
	{
		static Singleton instance;
		return instance;
	}

	void PrintSomething(const string& msg)
	{
		cout << msg << endl;
	}

private:
	Singleton()
	{
		cout << "Created " << endl;
	}

	Singleton(const Singleton&) = delete;

	Singleton& operator=(const Singleton&) = delete;

	~Singleton()
	{
		cout << "Destroyed " << endl;
	}

};

int main()
{
	Singleton::Instance().PrintSomething("msg 1");
	Singleton::Instance().PrintSomething("msg 2");
	Singleton::Instance().PrintSomething("msg 3");
}