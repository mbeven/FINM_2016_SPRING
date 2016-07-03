#include "AscendingList.h"
#include <iostream>
#include <string>

int main()
{
	midterm::AscendingList<int> list1; //Create list

	//Adds four values while maintaining ascending order
	list1.push(37);
	list1.push(20);
	list1.push(12);
	list1.push(21);

	//Prints out list
	list1.print();
}