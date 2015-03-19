#!/usr/bin/python

import csv
import sys
import getopt
import time
import codecs


options, remainder = getopt.getopt(sys.argv[1:], 'd:m:o:v',['dataset=','mapping=','output=','verbose','help'])
verbose = False
for opt,arg in options:
    if opt in ('-d', '--dataset'):
        datasetFilename = arg
    elif opt in ('-m', '--mapping'):
        mappingFilename = arg
    elif opt in ('-o', '--output'):
        outputFilename = arg
    elif opt in ('-v', '--verbose'):
        verbose = True
    elif opt in ('--help'):
        print "[HELP]"
        print "Try using: python %s  with the following parameters" % sys.argv[0]
        print "\t-d or --dataset <input_minimal_dataset>: required"
        print "\t-m or --mapping <mapping file>: required"
        print "\t-o or --output <output_mapping_file>: required"
        print "\t--verbose: optional"
        print "\t--help: optional"
        sys.exit()


'''
Cargar todos los internal_id de dataset en una lista
Recorrer linea por linea el mapping file
	si el internal_id es el mismo
		escribir linea en output
'''
startTime = time.time()

cont = 0
internal_ids = []
with open(datasetFilename) as datasetFile:
	dataRows = csv.DictReader(datasetFile)
	for row in dataRows:
		internal_ids.append(row['internal_id'])


total = len(internal_ids)
outputFile = codecs.open(outputFilename, "w", "iso-8859-1")
firstLine = "internal_id,dblp_id \n"
outputFile.write(firstLine)
if verbose:
	print firstLine.split('\n')[0]

with open(mappingFilename) as mappingFile:
	mappingRows = csv.DictReader(mappingFile)
	for mappingrow in mappingRows:
		if cont>=total:
			break
		if mappingrow['internal_id'] in internal_ids:
			outputLine = mappingrow['internal_id'] + "," + mappingrow['dblp_id '] + '\n'
			outputFile.write(outputLine)
			cont+=1
			if verbose:
				print outputLine.split('\n')[0]

outputFile.close()

print outputFilename,"generated in",int(time.time() - startTime),"seconds"

