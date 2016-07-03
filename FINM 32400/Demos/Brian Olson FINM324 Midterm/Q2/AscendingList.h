#ifndef ASCENDING_LIST_H
#define ASCENDING_LIST_H

#include <iostream>

using std::cout;
using std::endl;

namespace midterm
{
	template <typename T> //use template so any data type can be used
	class AscendingList
	{
	public:
		AscendingList(); //Constructor

		~AscendingList(); //Destructor

		void push(T value); //adds value to list and keeps ascending order

		void print(); //prints out entire list

	private:
		struct node
		{
			node(T val, node* n)
				: data(val), next(n)
			{}

			T data; //any data type
			node* next; //reference to next node
		};

		typedef node* link;

		link head; //Each list needs a head
	};

	//Constructor
	template <typename T>
	AscendingList<T>::AscendingList()
	{
		head = nullptr;
	}

	//Deconstructor
	template <typename T>
	AscendingList<T>::~AscendingList()
	{
		while (head)
		{
			link temp = head->next;
			delete head;
			head = temp;
		}
	}

	//This inserts a value while maintaining ascending order
	template <typename T>
	void AscendingList<T>::push(T val)
	{
		//if the list is empty, then we just start from the beginning
		if (!head)
		{
			head = new node(val, nullptr);
		}
		//if the head is greater than the value, then we just add at the beginning
		else if(head->data > val)
		{
			link temp = head;
			head = new node(val, nullptr);
			head->next = temp;
		}
		//otherwise, begin looping through list
		else
		{
			link temp = head;
			link prior = head;

			while (temp->data < val)  //stop when we reach a value greater than val
			{
				prior = temp;
				temp = temp->next;
			}
			prior->next = new node(val, temp); //create a new node inbetween prior and temp

		}
	}

	//This prints the entire list
	template <typename T>
	void AscendingList<T>::print()
	{
		node* temp = head;

		while (temp) //loop through list
		{
			cout << temp->data << endl; //print data
			temp = temp->next; //move to next value
		}
	}
}

#endif