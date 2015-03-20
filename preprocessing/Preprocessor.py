#!/usr/bin/python

import string
import time
import getopt
import sys
import codecs
import nltk
import csv
from collections import Counter
from collections import OrderedDict
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import SnowballStemmer


class Preprocessor:
	def __init__(self, inputFilename, output_path = ".", verbose = False, partition = None, counter = False, stem = None, filterPosTag = None):
		#params
		self.input_filename = inputFilename
		self.output_path = output_path
		self.verbose = verbose
		self.partition = partition
		self.showCounter = counter
		self.stemAlgorithm = stem
		self.filterPosTag = filterPosTag
		#class-defined
		self.tokens = []
		self.ocurrences = {}
		self.tagged_tokens = []
		

	def loadFromResource(self, resourceFilename):
		starTime = time.time()
		ocurrences = {}
		tokens = []
		with open(resourceFilename) as resourceFile:
			rows = csv.DictReader(resourceFile)
			for row in rows:
				ocurrences[row['token']] = row['frequency']
				tokens.append(row['token'])
		self.ocurrences = ocurrences
		self.tokens = tokens
		if self.verbose:
			print "\t... %d tokens load from %s in %d seconds" % (len(self.tokens), resourceFilename, int(time.time()-starTime))

	def isValidToken(self,token):
		if len(token) >= 4 and token not in stopwords.words('english') and not any(c.isdigit() for c in token):
			return True
		else:
			return False

	def execute(self):
		print "[START]"
		self.tokenizer()
		if self.filterPosTag != None:
			self.filterByPosTag(self.filterPosTag)
		if self.stemAlgorithm != None:
			self.stemmer()

	def tokenizer(self):
		tokens = []
		starTime = time.time()
		with open(self.input_filename) as stream:
			lines = stream.readlines()
			for line in lines:
				title = line.rstrip('\n').split(",")[2]
				#Adding every token in lower without punctuation, doesnt matther if duplicate or not
				[tokens.append(w) for w in nltk.word_tokenize(title.lower().translate(None, string.punctuation)) if self.isValidToken(w)]
		
		self.ocurrences = dict(Counter(tokens).most_common())
		self.tokens = list(set(tokens))
		
		if self.verbose:
			print "\t... found initially",len(self.tokens),"tokens in",int(time.time()-starTime),"seconds"

	def pos_tagger(self):
		starTime = time.time()
		self.tagged_tokens = dict(nltk.pos_tag(self.tokens))
		if self.verbose:
			print "\t... pos taggind finished in %d seconds" %(int(time.time()- starTime))
		

	def filterByPosTag(self, pos_tag):
		filtered = []
		ocurrencesFiltered = {}
		starTime = time.time()

		self.pos_tagger()

		for token in self.tokens:
			if self.tagged_tokens[token].startswith(pos_tag):
				filtered.append(token)
				ocurrencesFiltered[token] = self.ocurrences[token]
		
		self.tokens = filtered
		self.ocurrences = ocurrencesFiltered
		print "\t... %d tokens filtered by pos tag %s in %d seconds" %(len(self.tokens), pos_tag, int(time.time()-starTime))

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
		self.tokens = list(set(stemmed))
		print "\t...",len(self.tokens),"tokens stemmed (by "+self.stemAlgorithm+" algorithm) in",int(time.time() - starTime),"seconds"


	def exportTokensOrdered(self):
		starTime = time.time()
		fileTokens = codecs.open(self.output_path + "/tokens.txt", "w", "iso-8859-1")
		tokensOrdered = sorted(self.tokens)
		for token in tokensOrdered:
			fileTokens.write(token+"\n")
		fileTokens.close()
		if self.verbose:
			print "\t... %d tokens are written in %s/tokens.txt in %d seconds" % (len(self.tokens), self.output_path, int(time.time()-starTime))

	def exportTokenFrequency(self, threshold = 100):
		starTime = time.time()
		ocurrencesOrdered = OrderedDict(sorted(self.ocurrences.items(), key=lambda t: t[1], reverse=True))
		fileTokensFrequency = codecs.open(self.output_path+"/token_frequency.csv", "w", "iso-8859-1")
		line = "token,frequency\n"
		fileTokensFrequency.write(line)
		cont = 0
		for ocurrence in ocurrencesOrdered.items():
			if ocurrence[1] >= threshold:
				line = "%s,%d\n" %(ocurrence[0],ocurrence[1])
				fileTokensFrequency.write(line)
				cont+=1
		fileTokensFrequency.close()
		if self.verbose:
			print "\t... %d tokens with frequency greather than %d ocurrences are written in %s/token_frequency.csv in %d seconds" % (cont, threshold, self.output_path, int(time.time()-starTime))


