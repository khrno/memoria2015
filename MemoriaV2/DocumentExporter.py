#!/usr/bin/python
import gexf
import sys
import argparse
import ConfigParser
import time
import csv
import linecache
from os.path import isfile,join
from ParserLattice import Lattice


def documentExporter(latticeFilename, documentFilename, documentPath, intentExtended=False, tokensPath=None, 
	similarityPath=None, verbose=None):
	
	'''Reading Lattice'''
	if intentExtended:
		if verbose:
			print "Loading Lattice"
		lat = Lattice(latticefilename=latticeFilename, intentExtended=intentExtended, tokensPath=tokensPath, 
			similarityPath=similarityPath, verbose=verbose)
	else:
		print "[ERROR] intentExtended is set to False"
		return 0

	'''Exporting docs-concept'''
	if verbose:
		print "\nExporting document-titles for each concept"
	for concept in lat.concepts:
		

		documentConceptFilename = join(documentPath, "docs_%d.csv" % concept["id"])
		
		if verbose:
			print "\tExporting document titles of concept id %d" % concept['id'],
		with open(documentConceptFilename, "w") as documentFile:
			writer = csv.writer(documentFile, delimiter=",")
			header = ["year","document-title"]
			writer.writerow(header)
			for objectId in concept["extent"]:
				dindex = lat.getoObjectById(objectId)
				if dindex and len(dindex)>1:
					dindex = dindex[1:]
					try:
						dindex = int(dindex)
					except ValueError:
						print dindex, " could not be integer, passing to next" 
						pass

					line = linecache.getline(documentFilename, dindex)
					lineOriginal = line
					line = line.split(",")
					try:
						title = line[1].rsplit("\n")[0]
						year = line[0]
						writer.writerow([year, title])
					except IndexError:
						print "WARNING in concept %d, extent '%s' > index error" % (int(concept["id"]), lineOriginal)
						pass
		if verbose:
			print "\t[DONE]"

########################################################################################################################

# latticefilename = "Dataset/DBLP/ordered/0.5000/lattices/lattice.dblp.0.5000.ext.xml"
# documentfilename = "Dataset/DBLP/ordered/dblp.csv"
# documentpath = "Dataset/DBLP/ordered/0.5000/documents/"
# intentextended = True 
# tokenspath = "Dataset/DBLP/ordered/0.5000/tokens/"
# similaritypath = "Dataset/DBLP/ordered/0.5000/similarity/sims/"
# verbose = True

# documentExporter(latticefilename, documentfilename, documentpath, intentExtended=intentextended, tokensPath=tokenspath, 
# 	similarityPath=similaritypath, verbose=verbose)

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
	documentfilename = Config.get(sys.argv[0][:-3], "documentfilename")
	documentpath = Config.get(sys.argv[0][:-3], "documentpath")
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
	print "\tParameter documentfilename %s" % documentfilename
	print "\tParameter documentpath %s" % documentpath
	if intentextended:
		print "\tParameter intentextended activated"
	if tokenspath:
		print "\tParameter tokenspath %s" % tokenspath
	if similaritypath:
		print "\tParameter similaritypath %s" % similaritypath
	

	if args.timing:
		t0 = time.time()

	documentExporter(latticefilename, documentfilename, documentpath, intentExtended=intentextended, 
		tokensPath=tokenspath, similarityPath=similaritypath, verbose=args.verbose)

	if args.timing:
		t1 = time.time()
		print "Execution time: %0.3f seconds" % float(t1-t0)
	print "[END]"


