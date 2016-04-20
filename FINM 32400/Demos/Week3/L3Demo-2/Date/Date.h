#ifndef DATE_H
#define DATE_H

#include <ostream>

class Date
{
public:
	Date(int mm, int dd, int yyyy);

private:
	int day_;
	int month_;
	int year_;
};


#endif