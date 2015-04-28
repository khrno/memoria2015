//
// Created by Pablo Ortega Mesa on 13-04-15.
//

#include "FormalContext.hpp"
#include "csv.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <boost/algorithm/string.hpp> 
using namespace std;
using namespace khrno::FCA;
using namespace io;


void FormalContext::init(int nlimit){
	cout << "Execution Summary [c++]" << endl;
	cout << "+++++++++++++++++++++++++++++++++++++++++++++++++" << endl;
	

	std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();
	terms = loadTerms();
	std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();

	cout << "\tTerms:\t\t\t\t\t\t\t\t" << terms.size() << endl;
	cout << "\tTime reading terms file:\t\t\t" << (double)(std::chrono::duration_cast<std::chrono::microseconds>(t2 - t1).count())/1000000.0 << " seconds" <<endl;
	if(numTerms > 0 && terms.size() != numTerms){
		numTerms = terms.size();
	}

	documents = loadDocuments(nlimit);
	std::chrono::high_resolution_clock::time_point t3 = std::chrono::high_resolution_clock::now();
	cout << "\tDocs:\t\t\t\t\t\t\t\t" << documents.size() << endl;
	cout << "\tTime reading docs file:\t\t\t\t" << (double)(std::chrono::duration_cast<std::chrono::microseconds>(t3 - t2).count())/1000000.0 << " seconds" <<endl;
	if(numDocs > 0 && documents.size() != numDocs){
		numDocs = documents.size();
	}
	
	

}

vector<string> FormalContext::loadTerms(){
	vector<string> termsVector;
	string term;
	ifstream termFile(termsFilename);
	if (termFile.is_open()){
		while(getline(termFile,term)){
			termsVector.push_back(term);
		}
		termFile.close();
	}
	else{
		cout << "Unable to open terms file";
		return termsVector;
	}
	return termsVector;
}

vector<string> FormalContext::loadDocuments(int nlimit){
	vector<string> docsVector;
	CSVReader<3> in(docsFilename);
	// CSVReader<2> in(docsFilename);
	string title, sufix;
	int year, qty = 0;
	while(in.read_row(year, title, sufix)){

		boost::algorithm::to_lower(title);
		docsVector.push_back(title);
		qty++;
		if (nlimit>0 && qty == nlimit){
			break;
		}
	}
	return docsVector;
}

int** FormalContext::generateContext(){
	std::chrono::high_resolution_clock::time_point t1 = std::chrono::high_resolution_clock::now();
	int ** context;
	context = (int**) malloc(sizeof(int *) * numDocs);
	int i,j;
	int qty0 = 0;
	int qty1 = 0;
	string title, term;
	for (i = 0; i < numDocs; i++){
		context[i] = (int*) malloc(sizeof(int *) * numTerms);
		for(j=0; j < numTerms; j++){
			title = documents.at(i);
			term = terms.at(j);

			boost::algorithm::to_lower(term);
			boost::replace_first(term,"_"," ");
			boost::replace_first(term,"\n","");
			boost::replace_first(term,"\r","");
			// title to lower
			boost::algorithm::to_lower(title);
			// Check the ocurrence

			if(title.find(term) != string::npos){
				context[i][j] = 1;
				qty1++;
			}
			else{
				context[i][j] = 0;
				qty0++;
			}
		}
	}

	std::chrono::high_resolution_clock::time_point t2 = std::chrono::high_resolution_clock::now();
	cout << "\tFormal Context (#docs, #terms): \t(" << numDocs << "," << numTerms << ")" << endl;
	cout << "\tOnes found:\t\t\t\t\t\t\t" << qty1 << endl;
	cout << "\tZeros found:\t\t\t\t\t\t" << qty0 << endl;
	cout << "\tTime generating formal context:\t\t" << (double)(std::chrono::duration_cast<std::chrono::microseconds>(t2 - t1).count())/1000000.0 << " seconds" <<endl;
	binaryContext = context;
	return context;
}

void FormalContext::exportContextToCoronSystem(const string contextFilename){
	int i,j;
	string term;
	ofstream contextFile;
	contextFile.open (contextFilename);
	contextFile << "[Relational Context]" << endl;
	contextFile << "Default Name" << endl;
	contextFile << "[Binary Relation]"  << endl;
	contextFile << "Name_of_dataset" << endl;
	for(i = 0; i < (numDocs-1); i++){
		contextFile << "d" << (i+1) << " | ";
	}
	contextFile << "d" << (i+1) << endl;
	



	for(j = 0; j < (numTerms-1); j++){
		term = terms.at(j);
		// boost::replace_first(term,"_"," ");
		boost::replace_first(term,"\n","");
		boost::replace_first(term,"\r","");
		contextFile << term << " | ";
	}
	// cout << i << endl;
	term = terms.at(j);
	// // boost::replace_first(term,"_"," ");
	boost::replace_first(term,"\n","");
	boost::replace_first(term,"\r","");
	contextFile << term << endl;
	for(i = 0; i < numDocs; i++){
		for(j = 0; j < (numTerms-1); j++){
			contextFile << binaryContext[i][j] << " ";
		}
		contextFile << binaryContext[i][j] << endl;
	}
	contextFile << "[END Relational Context]" << endl;
	contextFile.close();
	cout << "exported to " << contextFilename << endl;

}

FormalContext::FormalContext(const string filename_terms, const string filename_documents, const int nlimit){
	termsFilename = filename_terms;
	docsFilename = filename_documents;
	init(nlimit);
	
}

FormalContext::FormalContext(const string filename_terms, const string filename_documents, const int num_terms, const int num_documents, const int nlimit){
	numDocs = num_documents;
	numTerms = num_terms;
	termsFilename = filename_terms;
	docsFilename = filename_documents;
	init(nlimit);
}

void FormalContext::print(){
	cout << "Terms filename: " << termsFilename << endl;
	cout << "Docs filename: " << docsFilename << endl;
	if (numTerms != -1){
		cout << "Num terms: " << numTerms << endl;
	} 
	if (numDocs != -1){
		cout << "Num docs: " << numDocs << endl;
	}
}