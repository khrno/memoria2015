#!/usr/bin/python

import xml.sax
import sys
import argparse
import ConfigParser
import time
from LatticeHandler import LatticeHandler

class Lattice():

	def __init__(self, latticefilename, verbose = False):
		'''Parser the lattice file'''
		parser = xml.sax.make_parser()
		parser.setFeature(xml.sax.handler.feature_namespaces, 0)
		parser.setFeature(xml.sax.handler.feature_external_ges, False)
		Handler = LatticeHandler(verbose)
		parser.setContentHandler(Handler)
		parser.parse(latticefilename)

		self.attributes = Handler.attributes
		self.objects = Handler.objects
		self.concepts = Handler.concepts
		self.stats = Handler.stats
		self.verbose = verbose

		self.getMaxLevel()

	def getMaxLevel(self):
		self.stats['max_level'] = -1
		for c in self.concepts:
			if c['level'] > self.stats['max_level']:
				self.stats['max_level'] = c['level']

	def getAttributeById(self, lookup):
		for attr in self.attributes:
			if attr['id'] == lookup:
				return attr['attr']
		return None

	def getObjectById(self, lookup):
		for obj in self.objects:
			if obj['id'] == lookup:
				return obj['obj']

	def getLatticeStats(self, statfilename):

		with open(statfilename, "w") as statFile:
			if self.verbose:
				print "Lattice Stats (written in %s)" % statfilename
				print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
				for k in self.stats.keys():

					if k == "nb_inner_nodes":
						print "\t%s: %s (+ 2 concepts bottom and top)" % (k, str(self.stats[k]))
					else:
						print "\t%s: %s" % (k, str(self.stats[k]))
			statFile.write("Lattice\n")
			for k in self.stats.keys():
				if k == "nb_inner_nodes":
					statFile.write("\t%s: %s (+ 2 concepts bottom and top)\n" % (k, str(self.stats[k])))
				else:
					statFile.write("\t%s: %s\n" % (k, str(self.stats[k])))

	def getLatticeSigmaJSFormat(self, sigmadatafilename):
		pass

if ( __name__ == "__main__"):
    argParser = argparse.ArgumentParser(description="Parse lattice xml file and get the stats of the lattice or write the lattice to json format to visualize it")
    
    argParser.add_argument("-v", "--verbose", action="store_true", 
        help="display each line to write in the csv file")
    argParser.add_argument("-t", "--timing", action="store_true",
        help="display the time of execution")
    argParser.add_argument("-c", "--config", type=str, required=True, 
        help="filepath to configuration file to read")
    args = argParser.parse_args()
    Config = ConfigParser.ConfigParser()
    Config.read(args.config)
    
    xmlfilename = Config.get(sys.argv[0][:-3], "xmlfilename")
    jsonfilename = Config.get(sys.argv[0][:-3], "jsonfilename")

    print "[START]"
    print "Parameter xmlfilename %s" % xmlfilename
    print "Parameter jsonfilename %s\n" % jsonfilename
    if args.timing:
        t0 = time.time()

	latt = Lattice(latticefilename=xmlfilename,verbose=args.verbose)

	statsfilename = xmlfilename.split(".xml")[0] + ".stats.txt"

	latt.getLatticeStats(statsfilename)

    if args.timing:
        t1 = time.time()
        print "Execution time: %0.3f seconds" % float(t1-t0)

    print "[END]"
