#!/usr/bin/python

import time
import getopt
import sys
import xml.sax

from DBLPHandler import DBLPHandler

if ( __name__ == "__main__"):
    verbose = False
    options, remainder = getopt.getopt(sys.argv[1:], 'i:o:vh',['input=','output=','verbose','help'])
    for opt,arg in options:
        if opt in ('-i', '--input'):
            input_filepath = arg
        elif opt in ('-o', '--output'):
            output_filepath = arg
        elif opt in ('-v', '--verbose'):
            verbose = True
        elif opt in ('-h', '--help'):
            print "[HELP]"
            print "Try using: python %s  with the following parameters" % sys.argv[0]
            print "\t-i or --input <input_filename>: required"
            print "\t-o or --output <output_filename>: required"
            print "\t-v or --verbose> optional"
            print "\t-h or --help: optional"
            sys.exit()

    starTime = time.time()

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = DBLPHandler(output_filepath, verbose)
    parser.setContentHandler(Handler)
    parser.parse(input_filepath)

    if verbose:
        print "Files DBLP.csv and MapIdsToDBLP.csv generated in",int(time.time() - starTime),"seconds"