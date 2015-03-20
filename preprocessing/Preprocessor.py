#!/usr/bin/python

import string
import time
import getopt
import sys
import codecs
import nltk
from collections import Counter
from collections import OrderedDict
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import SnowballStemmer


class Preprocessor:
	def __init__(self, inputFilename, output_path = ".", verbose = False, partition = None, counter = False, stem = "Porter"):
		#params
		self.input_filename = inputFilename
		self.output_path = output_path
		self.verbose = verbose
		self.partition = partition
		self.showCounter = counter
		self.stemAlgorithm = stem
		#class-defined
		self.tokens = []
		self.ocurrences = {}
		

	def execute(self):
		print "[START]"
		self.tokenizer()
		# self.stemmer()
		
		

	def tokenizer(self):
		tokens = []
		starTime = time.time()
		with open(self.input_filename) as stream:
			lines = stream.readlines()
			for line in lines:
				title = line.rstrip('\n').split(",")[2]
				#Adding every token in lower without punctuation, doesnt matther if duplicate or not
				[tokens.append(w) for w in nltk.word_tokenize(title.lower().translate(None, string.punctuation)) if not w in stopwords.words('english')]
		
		self.ocurrences = dict(Counter(tokens).most_common())
		self.tokens = list(set(tokens))
		self.duplicateTokens = tokens
		
		if self.verbose:
			print "\t... found initially",len(self.tokens),"tokens in",int(time.time()-starTime),"seconds"


	def stemmer(self):
		stemmed = []
		ocurrencesStemmed = {}
		starTime = time.time()
		
		for token in self.tokens:
			if self.stemAlgorithm == "Porter":
				stemmedToken = PorterStemmer().stem(token)
			elif self.stemAlgorithm == "Snowball":
				stemmedToken = SnowballStemmer('english').stem(token)
			elif self.stemAlgorithm == "Lancaster":
				stemmedToken = LancasterStemmer().stem(token)

			if stemmedToken in ocurrencesStemmed.keys():
				ocurrencesStemmed[stemmedToken] += self.ocurrences[token]
			else:
				ocurrencesStemmed[stemmedToken] = self.ocurrences[token]
			
			stemmed.append(stemmedToken)
		
		self.ocurrences = ocurrencesStemmed
		unique_stemmed = list(set(stemmed))
		print "\t...",len(unique_stemmed)," tokens stemmed (by "+stemAlgorithm+" algorithm) in",int(time.time() - starTime),"seconds"

	def exportTokenFrequency(self, filename, threshold = 100):
		starTime = time.time()
		ocurrencesOrdered = OrderedDict(sorted(self.ocurrences.items(), key=lambda t: t[1], reverse=True))
		fileTokensFrequency = codecs.open(self.output_path+"/"+filename, "w", "iso-8859-1")
		line = "token,frequency\n"
		fileTokensFrequency.write(line)
		cont = 0
		for ocurrence in ocurrencesOrdered.items():
			if ocurrence[1] >= threshold:
				line = "%s,%d\n" %(ocurrence[0],ocurrence[1])
				fileTokensFrequency.write(line)
				cont+=1
		fileTokensFrequency.close()
		if verbose:
			print "\t... %d tokens with frequency greather than %d ocurrences are written in %s/%s in %d seconds" % (cont, threshold, self.output_path, filename, int(time.time()-starTime))


if ( __name__ == "__main__"):
	verbose = False
	partition = None
	outputPath = "."
	counter = False
	stemAlgorithm = "Porter"
	fthreshold = 100
	options, remainder = getopt.getopt(sys.argv[1:], 'i:o:p:cvh',['input=','output=','partition=','stemPorter','stemLancaster','stemSnowball','fthreshold=','counter','verbose','help'])
	for opt,arg in options:
		if opt in ('-i', '--input'):
			inputFilename = arg

		elif opt in ('-o', '--output'):
			outputPath = arg

		elif opt in ('-p', '--partition'):
			partition = arg

		elif opt in ('--stemPorter'):
			stemAlgorithm = "Porter"

		elif opt in ('--stemLancaster'):
			stemAlgorithm = "Lancaster"

		elif opt in ('--stemSnowball'):
			stemAlgorithm = "Snowball"

		elif opt in('--fthreshold'):
			fthreshold = int(arg)
			
		elif opt in ('-c', '--counter'):
			counter = True

		elif opt in ('-v', '--verbose'):
			verbose = True

		elif opt in ('-h', '--help'):
			print "[HELP]"
			print "Try using: python %s  with the following parameters" % sys.argv[0]
			print "\t-i or --input <input_filename>: required"
			print "\t-o or --output <output_filename>: optional"
			print "\t--stemPorter or --stemLancaster --stemSnowball: optional"
			print "\t--fthreshold <frecuency_threshold>: optional"
			print "\t-p or --partition <partition type>: optional"
			print "\t-c or --counter output: optional"
			print "\t-v or --verbose: optional"
			print "\t-h or --help: optional"
			sys.exit()

	starTime = time.time()
	preprocessor = Preprocessor(inputFilename, outputPath, verbose, partition, counter, stemAlgorithm)
	
	preprocessor.execute()
	preprocessor.exportTokenFrequency('token_frequency.csv', fthreshold)

	print "\t... execution total time:",int(time.time() - starTime),"seconds"
	print "[DONE]"
