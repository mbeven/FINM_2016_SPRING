#include <iostream>
#include <sstream>
#include <fstream>
#include "IdHelper.h"

int IdHelper::orderId_ = 0;
int IdHelper::mdRequestId_ = 0;

IdHelper::IdHelper()
{
	orderId_ = ReadOrderIdFromFile();
}

IdHelper::~IdHelper()
{
	WriteOrderIdToFile();
}

void IdHelper::WriteOrderIdToFile()
{
	std::ofstream file("orderid.txt", std::ios::trunc);
	file << orderId_ << '\n';
}

int IdHelper::ReadOrderIdFromFile()
{
	std::ifstream file("orderid.txt");
	std::string s;
	std::getline(file, s);
	return s.empty() ? 0 : std::stoi(s);
}

std::string IdHelper::GetNextOrderId()
{
	orderId_++;
	std::stringstream s;
	s << orderId_;
	return s.str();
}

std::string IdHelper::GetCurrentOrderId()
{
	orderId_;
	std::stringstream s;
	s << orderId_;
	return s.str();
}

std::string IdHelper::GetNextMDRequestId()
{
	mdRequestId_++;
	std::stringstream s;
	s << mdRequestId_;
	return s.str();
}