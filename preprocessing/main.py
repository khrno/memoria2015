#!/usr/bin/python

import time
import getopt
import sys
from Preprocessor import Preprocessor

if ( __name__ == "__main__"):
	verbose = False
	partition = None
	outputPath = "."
	counter = False
	stemAlgorithm = None
	fthreshold = 100
	pos_tag_to_filter = None
	options, remainder = getopt.getopt(sys.argv[1:], 'i:o:p:t:cvh',['input=','output=','partition=','pos_tag=','stemPorter','stemLancaster','stemSnowball','fthreshold=','counter','verbose','help'])
	for opt,arg in options:
		if opt in ('-i', '--input'):
			inputFilename = arg

		elif opt in ('-o', '--output'):
			outputPath = arg

		elif opt in ('-p', '--partition'):
			partition = arg

		elif opt in ('--stemPorter'):
			stemAlgorithm = "Porter"

		elif opt in ('--stemLancaster'):
			stemAlgorithm = "Lancaster"

		elif opt in ('--stemSnowball'):
			stemAlgorithm = "Snowball"

		elif opt in ('-t', '--pos_tag'):
			pos_tag_to_filter = arg

		elif opt in('--fthreshold'):
			fthreshold = int(arg)
			
		elif opt in ('-c', '--counter'):
			counter = True

		elif opt in ('-v', '--verbose'):
			verbose = True

		elif opt in ('-h', '--help'):
			print "[HELP]"
			print "Try using: python %s  with the following parameters" % sys.argv[0]
			print "\t-i or --input <input_filename>: required"
			print "\t-o or --output <output_filename>: optional"
			print "\t--stemPorter or --stemLancaster --stemSnowball: optional"
			print "\t--fthreshold <frecuency_threshold>: optional"
			print "\t-t or --pos_tag <tag_to_filter>: optional"
			print "\t-p or --partition <partition type>: optional"
			print "\t-c or --counter output: optional"
			print "\t-v or --verbose: optional"
			print "\t-h or --help: optional"
			sys.exit()

	starTime = time.time()
	preprocessor = Preprocessor(inputFilename, outputPath, verbose, partition, counter, stemAlgorithm, pos_tag_to_filter)
	
	preprocessor.execute()
	preprocessor.exportTokenFrequency(fthreshold)
	preprocessor.exportTokensOrdered()
	print "\t... execution total time:",int(time.time() - starTime),"seconds"
	print "[DONE]"
