#include <iostream>
#include <fstream>
#include <vector>

// #include <boost/algorithm/string.hpp> 
#include "FormalContext.hpp"
// #include "csv.h"
using namespace std;
// using namespace io;
using namespace khrno::FCA;

const int max_num_terms = 194564;
const int max_num_documents = 2579465;

int main()
{


	std::chrono::high_resolution_clock::time_point start = std::chrono::high_resolution_clock::now();

	FormalContext fc("ajeoterms.txt", "data/dblp.csv", max_num_terms, max_num_documents, 0);
	fc.generateContext();
	fc.exportContextToCoronSystem("ajeo.context.rcf");
	std::chrono::high_resolution_clock::time_point end = std::chrono::high_resolution_clock::now();
	

	cout << "\tTotal time:\t\t\t\t\t\t\t" << (double)(std::chrono::duration_cast<std::chrono::microseconds>(end - start).count())/1000000.0 << " seconds" <<endl;
	cout << "+++++++++++++++++++++++++++++++++++++++++++++++++" << endl;

	return 0;
}