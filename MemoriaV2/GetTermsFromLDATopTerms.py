#!/usr/bin/python

import sys
import argparse
import ConfigParser
import time
import codecs
import csv
import nltk
import string
from unidecode import unidecode


class TermsGeneratorFromLDATopTerms():
	def __init__(self, termsfilename=None, verbose=False):
		self.bigramFrequency = {}
		self.bigrams = []
		self.termFrequency = {}
		self.terms = []
		self.qty = 0
		self.termsFilename = termsfilename
		if termsfilename != None:
			self.termsFile = codecs.open(self.termsFilename, "w", "iso-8859-1")
		self.verbose = verbose

	def loadTerms(self, ldafilename):
		with open(ldafilename, "rb") as ldafile:
			reader = csv.reader(ldafile, delimiter=",")
			header = reader.next()
			for row in reader:
				topic = row[0]
				words = row[1:]
				for word in words:
					self.terms.append(word)
					self.qty += 1
					self.termFrequency[word] = 0
		if self.verbose:
			print "%d lines loaded generating %d terms" % (len(self.terms),len(list(set(self.terms))))

		self.terms = list(set(self.terms))

	def exportTerms(self):
		for term in self.terms:
			self.termsFile.write("%s\n" % term)
		self.termsFile.close()

	def calculateTermFrequency(self, documentFilename):
		qty = 0
		with open(documentFilename, "rb") as documentFile:
			reader = csv.reader(documentFile, delimiter=",")
			for row in reader:
				qty += 1
				year = row[0]
				title = row[1]
				titleTokens = nltk.wordpunct_tokenize(title.lower().translate(None, string.punctuation))
				for term in self.terms:
					cleanTerm = term.translate(None, string.punctuation)
					if cleanTerm in titleTokens:
						self.termFrequency[term] += 1
				if self.verbose and qty % 100000 == 0:
					print "Still calculating term-frequencies (%d of %d)" % (qty, 2909316)
		if self.verbose:
			print "Max frequency found %d" % max(self.termFrequency.values())
			print "Min frequency found %d" % min(self.termFrequency.values())

	def writeTermFrequency(self, termFrequencyFilename):
		with open(termFrequencyFilename, "w") as termFrequencyFile:
			for term in self.termFrequency.keys():
				termFrequencyFile.write("%s,%s\n" % (term, self.termFrequency[term]))
		if self.verbose:
			print "Term frequency written in %s" % termFrequencyFilename

	def loadTermsAndTermsFrequencyFromFile(self, termFrequencyFilename):
		qty = 0
		with open(termFrequencyFilename, "rb") as termFrequencyFile:
			reader = csv.reader(termFrequencyFile, delimiter=",")
			for row in reader:
				self.termFrequency[row[0]] = int(row[1])
				self.terms.append(row[0])
		
		if self.verbose:
			print "%d terms loaded from %s" % (len(self.terms), termFrequencyFilename)
			print "Max frequency found %d" % max(self.termFrequency.values())
			print "Min frequency found %d" % min(self.termFrequency.values())

	def loadBigrams(self):
		print "\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
		print "Unimplemented, see reasons below"
		print "Problems detected"
		print "\t1) TMT returns orderer by frequency top terms, and no positional tokens"
		print "\t2) NLTK use positional tokens for build possible bigrams and calculate their frequency"
		print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"






if ( __name__ == "__main__"):
    argParser = argparse.ArgumentParser(description="Parse lda top terms output to generate a file with those terms")
    
    argParser.add_argument("-v", "--verbose", action="store_true", 
        help="display each term")
    argParser.add_argument("-t", "--timing", action="store_true",
        help="display the time of execution")
    argParser.add_argument("-c", "--config", type=str, required=True, 
        help="filepath to configuration file to read")
    argParser.add_argument("-g", "--generator", action="store_true", default=False,
    	help="generate term frequency instead of load from file")
    args = argParser.parse_args()
    

    Config = ConfigParser.ConfigParser()
    Config.read(args.config)

    ldatoptermsfilename = Config.get(sys.argv[0][:-3], "ldatoptermsfilename")
    termsfilename = Config.get(sys.argv[0][:-3], "termsfilename")
    documentfilename = Config.get(sys.argv[0][:-3], "documentfilename")
    if not args.generator:
    	termfrequencyfilename = Config.get(sys.argv[0][:-3], "termfrequencyfilename")


    print "[START]"
    print "Reading terms from %s" % ldatoptermsfilename
    print "Writing terms in %s" % termsfilename
    print "Reading docs from %s" % documentfilename
    print "Writing term frequency in %s" % termfrequencyfilename
    
    if args.timing:
    	t0 = time.time()

    if args.generator:
	    generator = TermsGeneratorFromLDATopTerms(termsfilename, args.verbose)
	    generator.loadTerms(ldatoptermsfilename)
	    generator.exportTerms()
	    generator.calculateTermFrequency(documentfilename)
	    generator.writeTermFrequency(termfrequencyfilename)
    else:
	    generator = TermsGeneratorFromLDATopTerms(verbose = args.verbose)
	    generator.loadTermsAndTermsFrequencyFromFile(termfrequencyfilename)


    if args.timing:
        t1 = time.time()
        print "Execution time: %0.3f seconds" % float(t1-t0)

    print "[END]"
