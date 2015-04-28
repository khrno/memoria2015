//
// Created by Pablo Ortega Mesa on 13-04-15.
//

#ifndef FCATOOL_FORMALCONTEXT_H
#define FCATOOL_FORMALCONTEXT_H

#include <iostream>
#include <vector>
using namespace std;

namespace khrno{
	namespace FCA{
		class FormalContext {
			private:
				string termsFilename;
				string docsFilename;
				int numTerms = -1;
				int numDocs = -1;
				vector<string> terms, documents;
				int** binaryContext;
				
				void init(int nlimit);
				vector<string> loadTerms();				
				vector<string> loadDocuments(int nlimit);
			public:
				FormalContext(const string filename_terms, const string filename_document, const int nlimit = 10);
				FormalContext(const string filename_terms, const string filename_document, const int num_terms, const int num_documents, const int nlimit = 10);

				// Tools
				int** generateContext();
				void exportContextToCoronSystem(const string contextFilename);
				
				// Display
				void print();
		};
	}
}

#endif //FCATOOL_FORMALCONTEXT_H