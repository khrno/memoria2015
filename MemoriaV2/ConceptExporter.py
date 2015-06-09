#!/usr/bin/python

import sys
import argparse
import ConfigParser
import time
import nltk
import os
from ParserLattice import Lattice
import csv


class ConceptExporter():
	def __init__(self, lattice, docsfilename, concept_log_filename="log.txt", 
		verbose=False, qtyVerboseConcept=10, conceptLimit=None, qtyVerboseExtent=100):
		self.verbose = verbose
		self.lattice = lattice
		self.docsFilename = docsfilename
		self.concept_log_filename = concept_log_filename
		self.qtyVerboseConcept = qtyVerboseConcept
		self.qtyVerboseExtent = qtyVerboseExtent
		self.conceptLimit = conceptLimit


		self.logged = self.loadConceptLog()

		self.docs = []
		self.loadDocs()
	
	def is_valid_token(self, token):
		tagged = dict(nltk.pos_tag([token]))
		if len(token) >= 4:
			if token not in stopwords.words('english'):
				if not any(c.isdigit() for c in token):
					if tagged[token].startswith('N'):
						return True
					else:
						return False
				else:
					return False
			else:
				return False
		else:
			return False

	def loadConceptLog(self):
		if os.path.exists(self.concept_log_filename):
			if self.verbose:
				print "Loading concept log"
			concepts = []
			with open(self.concept_log_filename, "r") as logFile:
				for line in logFile.readlines():
					idConcept = int(line)
					concepts.append(idConcept)
			
			if self.verbose:
				print "\t%d concepts loading from concept log" % len(concepts)

			return concepts
		return None

	def logConcept(self, id_concept):
		with open(self.concept_log_filename, "a") as logFile:
			logFile.write("\n%d" % id_concept)
			self.logged.append(id_concept)


	def loadDocs(self):
		if self.verbose:
			print "Loading Docs"
		qty = 0
		with open(self.docsFilename, "rb") as docsFile:
			reader = csv.reader(docsFile, delimiter=",")
			for row in reader:
				qty += 1
				title = row[1].split("\n")[0].split("\r")[0]
				self.docs.append(title)

		if self.verbose:
			print "\t%d docs loaded from %s" % (len(self.docs), self.docsFilename)

	def exportConcepts(self, path):
		if self.verbose:
			print "Exporting concepts"
		qty = 0
		for concept in self.lattice.concepts:
			if concept["type"] == "inner"  and (self.logged and len(self.logged)>0 and int(concept["id"]) not in self.logged):
			# if concept["type"] == "inner":
				text = ''
				filename = "%s/c_%d.txt" % (path, int(concept["id"]))
				i = 0
				if self.verbose and (qty == 0 or qty % self.qtyVerboseConcept == 0):
					print "\tProcesing concept %d of %d. Will be write in %s" % ((qty+1), (len(self.lattice.concepts)-2), filename)
				for extentIndex in concept["extent"]:
					i += 1
					if self.verbose and i % self.qtyVerboseExtent == 0:
						print "\t\tdoc %d of %d" % (i, len(concept["extent"]))
					dindex = self.lattice.getObjectById(extentIndex)
					if dindex and len(dindex)>1:
						dindex = dindex[1:]
						try:
							dindex = int(dindex)
						except ValueError:
							print dindex, " could not be integer, passing to next" 
							pass
						dindex = dindex - 1
						title = self.docs[dindex]
						text += " " + title
				
				with open(filename,"w") as conceptFile:
					conceptFile.write(text)

				self.logConcept(int(concept["id"]))
				qty += 1
			if self.conceptLimit and qty == self.conceptLimit: 
				break
		if self.verbose:
			print "\t%d concepts exported" % qty


if ( __name__ == "__main__"):
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
	conceptpath = Config.get(sys.argv[0][:-3], "conceptpath")
	conceptlogfilename = Config.get(sys.argv[0][:-3], "conceptlogfilename")
	qtyVerboseConcept = Config.get(sys.argv[0][:-3], "qtyVerboseConcept")
	qtyVerboseExtent = Config.get(sys.argv[0][:-3], "qtyVerboseExtent")
	conceptLimit = Config.get(sys.argv[0][:-3], "conceptLimit")

	qtyVerboseConcept = int(qtyVerboseConcept)
	qtyVerboseExtent = int(qtyVerboseExtent)
	conceptLimit = int(conceptLimit)


	print "[START]"
	print "Configuration:"
	print "\tParameter latticefilename %s" % latticefilename
	print "\tParameter documentfilename %s" % documentfilename
	print "\tParameter conceptpath %s" % conceptpath
	print "\tParameter conceptlogfilename %s" % conceptlogfilename
	print "\tParameter qtyVerboseConcept %d" % qtyVerboseConcept
	print "\tParameter qtyVerboseExtent %d" % qtyVerboseExtent
	print "\tParameter cocneptLimit %d" % conceptLimit

	if args.timing:
		t0 = time.time()

	if args.verbose:
		print "\nReading Lattice"

	latt = Lattice(latticefilename=latticefilename,verbose=args.verbose)
	exporter = ConceptExporter(latt,documentfilename, concept_log_filename=conceptlogfilename, 
		qtyVerboseConcept=qtyVerboseConcept, qtyVerboseExtent=qtyVerboseExtent, conceptLimit=conceptLimit, 
		verbose=args.verbose)
	exporter.exportConcepts(conceptpath)

	if args.timing:
		t1 = time.time()
		print "Execution time: %0.3f seconds" % float(t1-t0)

	print "[END]"
