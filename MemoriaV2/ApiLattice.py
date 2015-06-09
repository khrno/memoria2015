#!/usr/bin/python

import sys
import argparse
import ConfigParser
import time
import csv
import os
from ParserLattice import Lattice


class ApiLattice():
	def __init__(self, latticeFilename, documentFilename, verbose=False):
		self.latticeFilename = latticeFilename
		self.documentFilename = documentFilename
		self.verbose = verbose

		if self.verbose:
			print "\nReading Lattice"
		self.lattice = Lattice(latticefilename=self.latticeFilename, verbose=self.verbose)

		self.docs = []
		self.loadDocs()

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
	
	def showConceptExtent(self):
		i = 0
		for extentIndex in self.concept["extent"]:
			i += 1
			dindex = self.lattice.getObjectById(extentIndex)
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
				if i%10 == 0:
					raw_input("\n\t\tPress any key to continue...")

	def showConceptIntent(self):
		i = 0
		for intentIndex in self.concept["intent"]:
			i += 1
			token = self.lattice.getAttributeById(intentIndex)
			print "\t\t%d) %s" % (i, token)
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

			raw_input("\n\tPress any key to continue...")

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

	print "[START]"
	print "Configuration:"
	print "\tParameter latticefilename %s" % latticefilename
	print "\tParameter documentfilename %s" % documentfilename

	if args.timing:
		t0 = time.time()

	api = ApiLattice(latticefilename, documentfilename, verbose=args.verbose)
	api.menuGetConceptById()
	
	if args.timing:
		t1 = time.time()
		print "Execution time: %0.3f seconds" % float(t1-t0)

	print "[END]"
