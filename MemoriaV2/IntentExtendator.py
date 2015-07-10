import nltk
import string
import os
import sys
import argparse
import ConfigParser
import time
import csv
from nltk.corpus import stopwords

class IntentExtendator():
	def __init__(self, conceptDirectory, tokenDirectory, tokenFrequencyDirectory, concept_log_filename="log.txt", verbose=False):
		self.conceptDirectory = conceptDirectory
		self.tokenDirectory = tokenDirectory
		self.tokenFrequencyDirectory = tokenFrequencyDirectory
		self.concept_log_filename = concept_log_filename
		self.verbose = verbose

		if not self.conceptDirectory.endswith('/'):
			self.conceptDirectory += '/'
		if not self.tokenDirectory.endswith('/'):
			self.tokenDirectory += '/'

		self.logged = self.loadConceptLog()
		self.conceptFiles = self.makeConceptListToProcess()
		self.tokens = []

	def loadConceptLog(self):
		concepts = []
		if os.path.exists(self.concept_log_filename):
			if self.verbose:
				print "Loading concept log"
			with open(self.concept_log_filename, "r") as logFile:
				for line in logFile.readlines():
					idConcept = int(line)
					concepts.append(idConcept)
			
			if self.verbose:
				print "\t%d concepts loading from concept log" % len(concepts)

		return concepts

	def logConcept(self, id_concept):
		with open(self.concept_log_filename, "a") as logFile:
			logFile.write("\n%d" % id_concept)
			self.logged.append(id_concept)

	def conceptFilenameIsLogged(self, filename):
		conceptId = int(filename[2:].split(".txt")[0])
		return (conceptId in self.logged)


	def makeConceptListToProcess(self):
		if self.verbose:
			print "Reading concept files from path %s" % self.conceptDirectory

		conceptList = [ f 
			for f in os.listdir(self.conceptDirectory) 
				if os.path.isfile(os.path.join(self.conceptDirectory,f)) and 
					not f.startswith(".") and 
					not self.conceptFilenameIsLogged(f) ]

		if self.verbose:
			print "\t%d concept files loaded" % len(conceptList)

		return conceptList

	def applyFilters(self, tokens, filters):
		tokens_aux = tokens
		if 'pos_tag' in filters:
			tokens = self.applyPosTagFilter(tokens)
		if 'stopwords' in filters:
			tokens = self.applyStopwordsListFilter(tokens)
		if 'handcraft_stopwords':
			tokens = self.applyHandCraftStopwords(tokens, stopwordsfilename="stopwords_pom.txt")
		if 'len' in filters:
			tokens = self.applyTokenLenFilter(tokens)
		return tokens

	def applyPosTagFilter(self, tokens):
		if self.verbose:
			print "\t\tApplying pos tag filter",
		posTags = nltk.pos_tag(tokens)
		tokens_filtered = []
		for postag in posTags:
			if postag[1].startswith("N"):
				tokens_filtered.append(postag[0])
		if self.verbose:
			print "\t[Done]"
		return tokens_filtered

	def applyStopwordsListFilter(self, tokens):
		if self.verbose:
			print "\t\tApplying stopwords list filter",
		sstopwords = stopwords.words('english')
		tokens_filtered = []
		for token in tokens:
			if token not in sstopwords:
				tokens_filtered.append(token)
		if self.verbose:
			print "\t[Done]"
		return tokens_filtered

	def applyHandCraftStopwords(self, tokens, stopwordsfilename="stopwords.txt"):
		if self.verbose:
			print "\t\tApplying handcrafted stopword list:", stopwordsfilename,
		sstopwords = []
		with open(stopwordsfilename, "r") as swf:
			for word in swf:
				sstopwords.append(word.split("\n")[0])
		tokens_filtered = []
		for token in tokens:
			if token not in sstopwords:
				tokens_filtered.append(token)
		if self.verbose:
			print "\t[Done]"
		return tokens_filtered

	def applyTokenLenFilter(self, tokens, minLen=3):
		if self.verbose:
			print "\t\tApplying token len filter",
		tokens_filtered = []
		for token in tokens:
			if len(token) > minLen:
				tokens_filtered.append(token)
		if self.verbose:
			print "\t[Done]"
		return tokens_filtered

	def getConceptIdFromConceptFilename(self, filename):
		concept_id = int(filename[2:].split(".txt")[0])
		return concept_id

	def writeMostCommonTokens(self, tokens, conceptFilename, k = 50):
		concept_id = self.getConceptIdFromConceptFilename(conceptFilename)
		tokensFilename = "t_%d.txt" % concept_id
		fd = nltk.FreqDist(tokens)
		with open(os.path.join(self.tokenDirectory, tokensFilename), "w") as tokenFile:
			for t in fd.most_common(k):
				token = t[0]
				frequency = t[1]
				tokenFile.write("%s\n" % token)
		if self.verbose:
			print "\t\tTop %d Tokens written in %s" % (k,os.path.join(self.tokenDirectory, tokensFilename))

	def writeMostCommonTokensWithFrequency(self, tokens, conceptFilename, k = 50):
		concept_id = self.getConceptIdFromConceptFilename(conceptFilename)
		tokensFilename = "tf_%d.txt" % concept_id
		fd = nltk.FreqDist(tokens)
		with open(os.path.join(self.tokenFrequencyDirectory, tokensFilename), "w") as tokenFile:
			writer = csv.writer(tokenFile, delimiter=",")
			writer.writerow(['token','frequency'])
			for t in fd.most_common(k):
				token = t[0]
				frequency = t[1]
				writer.writerow([token, frequency])
		if self.verbose:
			print "\t\tTop %d Tokens-Frequency written in %s" % (k,os.path.join(self.tokenFrequencyDirectory, tokensFilename))

	def getTokens(self, breaklimit = None):
		qty = 0
		for conceptFilename in self.conceptFiles:
			if self.verbose:
				print "Processing concept file %s" % conceptFilename
			with open(os.path.join(self.conceptDirectory,conceptFilename),"r") as f:
				content = f.read()
			
			content = content.lower().translate(None, string.punctuation)
			tokens = nltk.wordpunct_tokenize(content)
			tokens = self.applyFilters(tokens, ['pos_tag','stopwords','handcraft_stopwords','len'])
			if self.verbose:
				print "\t%d tokens generated" % len(tokens)
			if self.verbose:
				print "\tWriting tokens in %s" % self.tokenDirectory
			self.writeMostCommonTokens(tokens,conceptFilename)
			self.writeMostCommonTokensWithFrequency(tokens, conceptFilename)

			self.logConcept(self.getConceptIdFromConceptFilename(conceptFilename))
			qty += 1
			if qty == breaklimit:
				break

	def generateStopwordListByTopKGlobalFrequencyDistribution(self, filename, k):
		globalTokens = []
		for concept_id in self.logged:
			tokensFilename = "t_%d.txt" % concept_id
			with open(os.path.join(self.tokenDirectory, tokensFilename), "r") as tokenFile:
				for token in tokenFile:
					token = token.split("\n")[0]
					globalTokens.append(token)
		fd = nltk.FreqDist(globalTokens)
		with open(filename, "a") as stopwordFile:
			for token in fd.most_common(k):
				print token
				stopwordFile.write("%s\n" % token[0] )
		fd.plot(30)

		print "Stopword list written in %s" % filename


if ( __name__ == "__main__"):
	argParser = argparse.ArgumentParser(
		description="Extends the intent of each concept applying NLP over the extent")

	argParser.add_argument("-v", "--verbose", action="store_true", 
		help="display each line to write in the csv file")
	argParser.add_argument("-t", "--timing", action="store_true",
		help="display the time of execution")
	argParser.add_argument("-c", "--config", type=str, required=True, 
		help="filepath to configuration file to read")
	args = argParser.parse_args()
	Config = ConfigParser.ConfigParser()
	Config.read(args.config)

	conceptdirectory = Config.get(sys.argv[0][:-3], "conceptdirectory")
	tokendirectory = Config.get(sys.argv[0][:-3], "tokendirectory")
	tokenfrequencydirectory =  Config.get(sys.argv[0][:-3], "tokenfrequencydirectory")
	conceptlogfilename = Config.get(sys.argv[0][:-3], "conceptlogfilename")
	breaklimit = Config.get(sys.argv[0][:-3], "breaklimit")
	
	breaklimit = int(breaklimit)

	print "[START]"
	print "Configuration:"
	print "\tParameter conceptdirectory %s" % conceptdirectory
	print "\tParameter tokendirectory %s" % tokendirectory
	print "\tParameter tokenfrequencydirectory %s" % tokenfrequencydirectory
	print "\tParameter conceptlogfilename %s" % conceptlogfilename
	print "\tParameter breaklimit %d" % breaklimit

	if args.timing:
		t0 = time.time()

	extendator = IntentExtendator(conceptdirectory, tokendirectory, tokenfrequencydirectory, concept_log_filename=conceptlogfilename, verbose=args.verbose)
	extendator.getTokens(breaklimit)
	# extendator.generateStopwordListByTopKGlobalFrequencyDistribution("stopwords.txt", 5)

	if args.timing:
		t1 = time.time()
		print "Execution time: %0.3f seconds" % float(t1-t0)

	print "[END]"

