#include "Application.h"

#include <quickfix/FileStore.h>
#include <quickfix/SocketInitiator.h>
#include <quickfix/SessionSettings.h>
#include <quickfix/FileLog.h>

#include <string>
#include <iostream>
#include <fstream>

using std::cerr;
using std::endl;

int main()
{
  std::string file = "../config/tt.cfg";

  try
  {
	Application app(file);
	
	app.Init();

	app.Run();
  }
  catch (std::exception & e)
  {
	 cerr << "Exception Caught: " << e.what() << std::endl;
  }
}
