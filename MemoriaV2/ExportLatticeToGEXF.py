#!/usr/bin/python
import gexf
import sys
import argparse
import ConfigParser
import time
from ParserLattice import Lattice


def exportLattice(latticeFilename, gexffilename, latticeDescription=None, topK=5,intentExtended=False, tokensPath=None, 
	similarityPath=None, verbose=None):
	
	
	lat = Lattice(latticefilename=latticeFilename, intentExtended=intentExtended, tokensPath=tokensPath, similarityPath=similarityPath, verbose=verbose)

	if verbose:
		print "\tExporting Lattice to GEXF....",

	lat.exportLatticeToGEXFFormat(outputFilename=gexffilename,topK=topK, description=latticeDescription)

	if verbose:
		print "[DONE]"


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
	gexffilename = Config.get(sys.argv[0][:-3], "gexffilename")
	try:
		latticedescription = Config.get(sys.argv[0][:-3],"latticedescription")
	except ConfigParser.NoOptionError:
		latticedescription = None
	try:
		topk = Config.getint(sys.argv[0][:-3],"topk")
	except ConfigParser.NoOptionError:
		topk = 5
	try:
		intentextended = Config.getboolean(sys.argv[0][:-3], "intentextended")
	except ConfigParser.NoOptionError:
		intentextended=False
	try:
		tokenspath =  Config.get(sys.argv[0][:-3], "tokenspath")
	except ConfigParser.NoOptionError:
		tokenspath = None
	try:
		similaritypath =  Config.get(sys.argv[0][:-3], "similaritypath") 
	except ConfigParser.NoOptionError:
		similaritypath = None

	print "[START]"
	print "Configuration:"
	print "\tParameter latticefilename %s" % latticefilename
	print "\tParameter gexffilename %s" % gexffilename
	if latticedescription:
		print "\tParameter gexffilename %s" % latticedescription
	if topk:
		print "\tParameter topk %d" % topk
	if intentextended:
		print "\tParameter intentextended activated"
	if tokenspath:
		print "\tParameter tokenspath %s" % tokenspath
	if similaritypath:
		print "\tParameter similaritypath %s" % similaritypath
	

	if args.timing:
		t0 = time.time()

	exportLattice(latticefilename, gexffilename, latticeDescription=latticedescription, topK=topk,
		intentExtended=intentextended, tokensPath=tokenspath, similarityPath=similaritypath, verbose=args.verbose)

	if args.timing:
		t1 = time.time()
		print "Execution time: %0.3f seconds" % float(t1-t0)
	print "[END]"

