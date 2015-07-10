#!/usr/bin/python

import sys
import argparse
import ConfigParser
import time
import csv
import os

import numpy
import nltk
import string

from ParserLattice import Lattice


class ApiLattice():
	def __init__(self, latticeFilename, documentFilename, intentExtent=False, tokensPath=None, simmilarityFile=None, verbose=False):
		self.latticeFilename = latticeFilename
		self.documentFilename = documentFilename
		self.verbose = verbose

		if self.verbose:
			print "\nReading Lattice"

		if intentExtent:
			self.lattice = Lattice(latticefilename=self.latticeFilename, intentExtended=True, tokensPath = tokensPath, verbose=self.verbose)
		else:
			self.lattice = Lattice(latticefilename=self.latticeFilename, verbose=self.verbose)

		if simmilarityFile:
			self.loadSimilarity(simmilarityFile)
		else:
			self.topics = None

		self.docs = []
		self.loadDocs()

	def loadSimilarity(self, simmilarityFilename):
		if self.verbose:
			print "Loading similarity jaccard"
		topics = []
		with open(simmilarityFilename, "rb") as simFile:
			reader = csv.reader(simFile, delimiter=",")
			reader.next() # skip header
			for row in reader:
				topicName = str(row[0])
				conceptId = str(row[1])
				simValue = float(row[2])
				if topicName not in topics:
					topics.append(topicName)

				concept = self.getConceptById(int(conceptId))
				if "topicDistribution" not in concept.keys():
					concept["topicDistribution"] = []
				
				simTuple = (simValue, topicName)
				concept["topicDistribution"].append(simTuple)
		for concept in self.lattice.concepts:
			if "topicDistribution" in concept.keys():
				concept["topicDistribution"].sort(reverse=True)

		self.topics = topics
		if self.verbose:
			print "\t%d topics loaded" % len(topics)

	def loadDocs(self):
		if self.verbose:
			print "Loading Docs"
		qty = 0
		with open(self.documentFilename, "rb") as docsFile:
			reader = csv.reader(docsFile, delimiter=",")
			for row in reader:
				qty += 1
				title = row[1].split("\n")[0].split("\r")[0]
				self.docs.append(title)

		if self.verbose:
			print "\t%d docs loaded from %s" % (len(self.docs), self.documentFilename)

	def getConceptById(self, idConcept):
		for concept in self.lattice.concepts:
			if int(concept["id"]) == idConcept:
				return concept
		return None

	def showLatticeMaxLevel(self):
		maxlevel = -1
		for concept in self.lattice.concepts:
			if int(concept["level"]) > maxlevel:
				maxlevel = int(concept["level"])
		print maxlevel
		raw_input("\n\t\tPress any key to continue...")
	
	def showConceptExtent(self):
		i = 0
		for extentIndex in self.concept["extent"]:
			i += 1
			dindex = self.lattice.getoObjectById(extentIndex)
			if dindex and len(dindex)>1:
				dindex = dindex[1:]
				try:
					dindex = int(dindex)
				except ValueError:
					print "\t\t[warning]",dindex, " could not be integer, passing through" 
					pass
				dindex = dindex - 1
				title = self.docs[dindex]
				print "\t\t%d) %s" % (i, title)
				# if i%10 == 0:
				# 	raw_input("\n\t\tPress any key to continue...")

	def showConceptIntent(self):
		i = 0
		for intentIndex in self.concept["intent"]:
			i += 1
			token = self.lattice.getAttributeById(intentIndex)
			print "\t\t%d) %s" % (i, token)
			if i%10 == 0:
				raw_input("\n\t\tPress any key to continue...")

	def showTopics(self):
		i = 0
		for topic in self.topics:
			i += 1
			print "\t\t%d) %s" % (i, topic)
			if i%10 == 0:
				raw_input("\n\t\tPress any key to continue...")

	def showMenuExecuteAction(self):
		option = -1
		while option != 8:
			os.system('clear')
			print "\tMenu (concept id %d)" % self.concept["id"]
			print "\t+++++++++++++++++++++++++++++++++++++"
			print "\t1) Number of elements in extent"
			print "\t2) Number of elements in intent"
			print "\t3) Type of the concept"
			print "\t4) Level of the concept"
			print "\t5) Absolute support of the concept"
			print "\t6) Get the extent (press space each 10 elements)"
			print "\t7) Get the intent (press space each 10 elements)"
			print "\t8) Return to the main menu"
			print "\t9) Get the max level of the lattice"
			print "\t10) Seleccionar el top concept"
			print "\t11) Seleccionar el bottom concept"
			if self.topics and len(self.topics) > 0:
				print "\t12) Get top 5 topics (jaccard simmilarity)"
				print "\t13) Get topics (press space each 10 elements)"
			print "\t14) Generate concept context"

			print "\n\tIngrese su opcion:",
			try:
				option = int(raw_input())
			except ValueError:
				print "\t[ERROR] Por favor ingrese un numero del 1 al 8"

			if option==1:
				print "\n\t\t# Extent = %d" % len(self.concept["extent"])
			elif option==2:
				print "\n\t\t# Intent = %d" % len(self.concept["intent"])
			elif option==3:
				print "\n\t\tType = %s" % self.concept["type"]
			elif option==4:
				print "\n\t\tLevel = %d" % self.concept["level"]
			elif option==5:
				print "\n\t\tSupp Abs = %d" % self.concept["supp_abs"]
			elif option==6:
				self.showConceptExtent()
			elif option==7:
				self.showConceptIntent()
			elif option==8:
				break
			elif option==9:
				self.showLatticeMaxLevel()
			elif option==10:
				self.concept = None
				self.concept = self.getTopConcept()
				self.showMenuExecuteAction()
			elif option==11:
				self.concept = None
				self.concept = self.getBottomConcept()
				self.showMenuExecuteAction()
			elif option==12:
				self.showTopTopcisOfConcept(5)
			elif option==13:
				self.showTopics()
			elif option==14:
				self.generateConceptContext()

			raw_input("\n\tPress any key to continue...")
	
	def showTopTopcisOfConcept(self, k):
		print "\t\t%d Topcis of Concept %d" % (k,int(self.concept["id"]))
		print "\t\t+++++++++++++++++++++++++++++"
		if self.concept["type"] == "inner":
			for i in range(0,k):
				print "\t\t%d) %s -> %f" % ((i+1),self.concept["topicDistribution"][i][1],self.concept["topicDistribution"][i][0])


	def getTopConcept(self):
		for concept in self.lattice.concepts:
			if concept["type"] == "top":
				return concept
		return None

	def getBottomConcept(self):
		for concept in self.lattice.concepts:
			if concept["type"] == "bottom":
				return concept
		return None

	def menuGetConceptById(self, level=1):
		idConcept = -1
		while idConcept != 'q':
			os.system('clear')
			print "API Lattice Menu"
			print "+++++++++++++++++"
			print "\tEnter concept id or 'q' for quit ",
			idConcept = raw_input()
			if idConcept != 'q':
				idConcept = int(idConcept)
			
			concept = self.getConceptById(idConcept)
			if concept:
				self.concept = concept
				self.showMenuExecuteAction()
			else:
				print "Concept dont exist"
	
	def getObjectByExtentIndex(self, lookup):
		dindex = self.lattice.getObjectById(lookup) # dindex have format d+indexdoc
		if dindex and len(dindex)>1:
			dindex = dindex[1:] # removing first letter 'd'
			try:
				dindex = int(dindex)
			except ValueError:
				print "[WARNING]",dindex,"is not integer. Passing through"
				return None
			dindex = dindex - 1
			title = self.docs[dindex]
			return title
		else:
			print "[WARNING]",dindex,"is not found or incorrect format. Passing through"
			return None

	def generateConceptContext(self, filename="context"):
		if self.concept["type"] != "inner":
			print "Concept type must be 'inner'"
			return False

		filename = "extent%d.txt" % self.concept["id"]
		with open(filename,"w") as f:
			for i in range(0,len(self.concept["extent"])):
				index = self.concept["extent"][i]
				f.write("%s\n" % index)
			

		
			# for i in range(0,len(documentIndexes)):
			# 	f.write("%d\n" % documentIndexes[i])
		print "done"

		# dimensions = (len(self.concept["extent"]), len(self.concept["intent"]))
		# context = numpy.zeros(dimensions, dtype=numpy.int)
		# for i in range(0,len(self.concept["extent"])):
		# 	docTitle = self.getObjectByExtentIndex(self.concept["extent"][i])
		# 	if docTitle != None:
		# 		docTokens = nltk.wordpunct_tokenize(docTitle.lower().translate(None, string.punctuation))
		# 		for j in range(0,len(self.concept["intent"])):
		# 			token = self.lattice.getAttributeById(self.concept['intent'][j])
		# 			if token in docTokens:
		# 				context[i][j] = 1
		# print context




if ( __name__ == "__main__"):
	os.system('clear')
	argParser = argparse.ArgumentParser(
		description="Parse lattice xml file and get the stats of the lattice or write the "+
		"lattice to json format to visualize it")

	argParser.add_argument("-v", "--verbose", action="store_true", 
		help="display each line to write in the csv file")
	argParser.add_argument("-t", "--timing", action="store_true",
		help="display the time of execution")
	argParser.add_argument("-c", "--config", type=str, required=True, 
		help="filepath to configuration file to read")
	args = argParser.parse_args()
	Config = ConfigParser.ConfigParser()
	Config.read(args.config)

	latticefilename = Config.get(sys.argv[0][:-3], "latticefilename")
	documentfilename = Config.get(sys.argv[0][:-3], "documentfilename")
	try:
		intentextended = Config.getboolean(sys.argv[0][:-3],"intentextended")
	except ConfigParser.NoOptionError:
		intentextended = False

	try:
		tokenspath = Config.get(sys.argv[0][:-3], "tokenspath")
	except ConfigParser.NoOptionError:
		tokenspath = None

	try:
		simmilarityfile = Config.get(sys.argv[0][:-3], "simmilarityfile")
	except ConfigParser.NoOptionError:
		simmilarityfile = None

	print "[START]"
	print "Configuration:"
	print "\tParameter latticefilename %s" % latticefilename
	print "\tParameter documentfilename %s" % documentfilename
	if intentextended:
		print "\tParameter intentextended activated"
	if tokenspath:
		print "\tParameter tokenspath %s" % tokenspath
	if simmilarityfile:
		print "\tParameter simmilarityfile %s" % simmilarityfile

	if args.timing:
		t0 = time.time()

	api = ApiLattice(latticefilename, documentfilename, intentExtent=intentextended, tokensPath=tokenspath, simmilarityFile=simmilarityfile, verbose=args.verbose)
	api.menuGetConceptById()
	
	if args.timing:
		t1 = time.time()
		print "Execution time: %0.3f seconds" % float(t1-t0)

	print "[END]"
