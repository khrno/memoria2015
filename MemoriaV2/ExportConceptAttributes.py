#!/usr/bin/python

import json
import sys
import argparse
import ConfigParser
import time
from os.path import isfile,join
from ParserLattice import Lattice


class ConceptAttributes():
	def __init__(self, latticeFilename, targetPath, verbose):
		self.latticeFilename = latticeFilename
		self.targetPath = targetPath
		self.verbose = verbose

		self.lattice = self.loadLattice()

	def loadLattice(self):
		if self.verbose:
			print "Loading Lattice"	
		lat = Lattice(latticefilename=self.latticeFilename, verbose=self.verbose)
		return lat

	def getNeighborhood(self, concept):
		parents = concept["parents"]
		children = concept["children"]
		top = None
		bottom = None
		right = None
		left = None
		conceptsByLevel = self.lattice.getConceptsByLevel(concept["level"],True)
		for i in range(0,len(conceptsByLevel)):
			if conceptsByLevel[i]["id"] == concept["id"]:
				break
		if i>0:
			left = conceptsByLevel[i-1]["id"]

		if i<(len(conceptsByLevel))-1:
			right = conceptsByLevel[i+1]["id"]

		if len(parents)>0:
			top = int(parents[0])

		if len(children)>0:
			bottom = int(children[0])
		
		return top,right,bottom,left
	
	

	def exportConceptAttributes(self):
		for concept in self.lattice.concepts:
			top,right,bottom,left = self.getNeighborhood(concept)
			properties = {
				"id"				: concept["id"],
				"supp_abs"			: concept["supp_abs"],
				"level"				: concept["level"],
				"extent"			: len(concept["extent"]),
				"intentBase"		: len(concept["intent"]),
				"intentExtended"	: 50,
				"type"				: concept["type"],
				"top"				: top,
				"bottom"			: bottom,
				"left"				: left,
				"right"				: right
			}
			filename = join(self.targetPath, "attrs_%d.json" % concept["id"])
			with open(filename, "w") as fileAttr:
				json.dump({"properties":properties}, fileAttr)
		if self.verbose:
			print "%d concepts attributes written in %s" % (len(self.lattice.concepts), self.targetPath)

########################################################################################################################
			
# ca = ConceptAttributes("Dataset/DBLP/ordered/0.5000/lattices/lattice.dblp.0.5000.ext.xml", "Dataset/DBLP/ordered/0.5000/attributes/", True)
# ca.exportConceptAttributes()

########################################################################################################################

if ( __name__ == "__main__"):
	argParser = argparse.ArgumentParser(
		description="Export lattice to GEXF format to visualize it in GEPHI software")

	argParser.add_argument("-v", "--verbose", action="store_true", 
		help="display each line to write in the csv file")
	argParser.add_argument("-t", "--timing", action="store_true",
		help="display the time of execution")
	argParser.add_argument("-c", "--config", type=str, required=True, 
		help="filepath to configuration file to read")
	args = argParser.parse_args()
	Config = ConfigParser.ConfigParser()
	Config.read(args.config)


	'''reading configuration'''
	latticefilename = Config.get(sys.argv[0][:-3], "latticefilename")
	targetpath = Config.get(sys.argv[0][:-3], "targetpath")

	print "[START]"
	print "Configuration:"
	print "\tParameter latticefilename %s" % latticefilename
	print "\tParameter targetpath %s" % targetpath
	

	if args.timing:
		t0 = time.time()

	ca = ConceptAttributes(latticefilename, targetpath, args.verbose)
	ca.exportConceptAttributes()

	if args.timing:
		t1 = time.time()
		print "Execution time: %0.3f seconds" % float(t1-t0)
	
	print "[END]"


