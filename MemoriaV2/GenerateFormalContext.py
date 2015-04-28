#!/usr/bin/python

import sys
import argparse
import ConfigParser
import time
import csv
import nltk
import string
import numpy as np

class FormalContext():
	def __init__(self, termsfilename, docsfilename, verbose=False, dlimit=-1, tlimit=-1):
		self.termsFilename = termsfilename
		self.docsFilename = docsfilename
		self.verbose = verbose
		self.dlimit = dlimit
		self.tlimit = tlimit

		self.terms = []
		self.docs = []

		self.loadTerms()
		self.loadDocs()

		self.context = None

	def loadTerms(self):
		qty = 0
		with open(self.termsFilename, "r") as termsFile:
			for term in termsFile:
				qty += 1
				term = term.split("\n")[0].split("\r")[0]
				self.terms.append(term)
				if self.tlimit>0 and qty==self.tlimit:
					break
		if self.verbose:
			print "%d terms loaded from %s" % (len(self.terms), self.termsFilename)

	def loadDocs(self):
		qty = 0
		with open(self.docsFilename, "rb") as docsFile:
			reader = csv.reader(docsFile, delimiter=",")
			for row in reader:
				qty += 1
				title = row[1].split("\n")[0].split("\r")[0]
				self.docs.append(title)
				if self.dlimit>0  and qty==self.dlimit:
					break

		if self.verbose:
			print "%d docs loaded from %s" % (len(self.docs), self.docsFilename)

	def generateContext(self):
		qty = 0
		context = np.zeros((len(self.docs), len(self.terms)), dtype=np.int)
		ones_counter = 0
		for i in range(0,len(self.docs)):
			qty += 1
			docTokens = nltk.wordpunct_tokenize(self.docs[i].lower().translate(None, string.punctuation))
			for j in range(0, len(self.terms)):
				cleanTerm = self.terms[j].translate(None, string.punctuation)
				if cleanTerm in docTokens:
					context[i][j] = 1
					ones_counter += 1
			if self.verbose and qty % 100000 == 0:
				print "Still generate formal context (%d of %d)" % (qty, len(self.docs))

		self.context = np.transpose(context)

		if self.verbose:
			print "Context generated %dx%d" % (self.context.shape[0], self.context.shape[1])
			print "\t%d ones found" % ones_counter
			print "\t%d zeros found" % ((len(self.docs)*len(self.terms)) - ones_counter)

	def exportContextToCoron(self, coroncontextfilename):
		with open(coroncontextfilename, "w") as coronFile:
			coronFile.write("[Relational Context]\n")
			coronFile.write("Default Name\n")
			coronFile.write("[Binary Relation]\n")
			coronFile.write("Name_of_dataset\n")
			for i in range(1, len(self.docs)):
				coronFile.write("d%d | " % i)
			coronFile.write("d%d \n" % len(self.docs))
			for i in range(1, len(self.terms)):
				j = i-1
				coronFile.write("%s | " % self.terms[j])
			coronFile.write("%s\n" % self.terms[len(self.terms)-1])

			coroncontext = np.transpose(self.context)
			
			print self.context.shape
			for i in range(0, len(self.docs)):
				for j in range(0, len(self.terms) -1):
					coronFile.write("%d " % coroncontext[i][j])
				coronFile.write("%d\n" % coroncontext[i][(len(self.terms)-1)])
				if self.verbose and i>0 and i % 100000 == 0:
					print "Still writing formal context to coron (%d of %d)" % (i, len(self.docs))

			coronFile.write("[END Relational Context]\n")

	def exportContextToSephirot(self, sephirotcontextfilename):
		with open(sephirotcontextfilename, "w") as sephirotFile:
			sephirotContext = np.transpose(self.context)
			for i in range(0, len(self.docs)):
				attrs = []
				for j in range(0, len(self.terms) ):
					if sephirotContext[i][j] == 1:
						attrs.append(self.terms[j])
					sephirotFile.write("%s\n" % (",".join(attrs)))
				if self.verbose and i>0 and i % 100000 == 0:
					print "Still writing formal context to sephirot (%d of %d)" % (i, len(self.docs))




if ( __name__ == "__main__"):
    argParser = argparse.ArgumentParser(description="Generate formal context in differentes formats to use in several systems (coron and sephirot at the moment)")
    
    argParser.add_argument("-v", "--verbose", action="store_true", 
        help="display each term")
    argParser.add_argument("-t", "--timing", action="store_true",
        help="display the time of execution")
    argParser.add_argument("--skipcoron", action="store_true", 
    	help="skip write context to coron format")
    argParser.add_argument("--skipsephirot", action="store_true",
    	help="skip write context to sephirot format")
    argParser.add_argument("-c", "--config", type=str, required=True, 
        help="filepath to configuration file to read")
    args = argParser.parse_args()

    dlimit = -1
    tlimit = -1

    Config = ConfigParser.ConfigParser()
    Config.read(args.config)

    termsfilename = Config.get(sys.argv[0][:-3], "termsfilename")
    docsfilename = Config.get(sys.argv[0][:-3], "docsfilename")
    
    if not args.skipcoron:
    	coronfilename = Config.get(sys.argv[0][:-3], "coronfilename")

    if not args.skipsephirot:
    	sephirotfilename = Config.get(sys.argv[0][:-3], "sephirotfilename")
    
    if Config.has_option(sys.argv[0][:-3], "dlimit"):
    	dlimit = Config.getint(sys.argv[0][:-3], "dlimit")
    

	if Config.has_option(sys.argv[0][:-3], "tlimit"):
		tlimit = Config.getint(sys.argv[0][:-3], "tlimit")
	


    print "[START]"
    print "Reading terms from %s" % termsfilename
    print "Reading docs from %s" % docsfilename
    if not args.skipcoron:
    	print "Writing context in coron format in %s" % coronfilename
    if not args.skipsephirot:
    	print "Writing context in sephirot format in %s" % sephirotfilename
    if dlimit > 0:
    	print "With documents limit of %d" % dlimit

    if tlimit > 0:
    	print "With terms limit of %d" % tlimit
    
    if args.timing:
    	t0 = time.time()

    fc = FormalContext(termsfilename = termsfilename, docsfilename = docsfilename, verbose = args.verbose, dlimit=dlimit, tlimit=tlimit)
    fc.generateContext()
    if not args.skipcoron:
    	fc.exportContextToCoron(coronfilename)
    if not args.skipsephirot:
    	fc.exportContextToSephirot(sephirotfilename)

    if args.timing:
        t1 = time.time()
        print "Execution time: %0.3f seconds" % float(t1-t0)

    print "[END]"