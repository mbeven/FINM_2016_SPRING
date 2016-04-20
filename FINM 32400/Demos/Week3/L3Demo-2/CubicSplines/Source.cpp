#include <cmath>
#include <iostream>

#include <gsl/gsl_errno.h>
#include <gsl/gsl_spline.h>


void TestInterpolationSpline()
{
	double x[5], y[5];  //need to store 'x' and 'y' values in two arrays

	x[0] = 1.0; y[0] = 2.4;
	x[1] = 1.3; y[1] = 4.6;
	x[2] = 1.4; y[2] = 4.7;
	x[3] = 1.8; y[3] = 2.3;
	x[4] = 2.0; y[4] = 1.0;

	gsl_interp_accel *acc= gsl_interp_accel_alloc();
	gsl_spline *spline = gsl_spline_alloc(gsl_interp_cspline, 5); //5 <= number of data points

	gsl_spline_init(spline, x, y, 5);  //initilize the spline

	double x1 = 1.3;
	double y1 = gsl_spline_eval(spline, x1, acc);  //get 'y1' for any 'x1'

	std::cout << y1 << std::endl;

	gsl_spline_free(spline);
	gsl_interp_accel_free(acc);
	
}

int main()
{
	TestInterpolationSpline();
}

