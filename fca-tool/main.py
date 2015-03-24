#!/usr/bin/python

import time
import getopt
import sys
import xml.sax

from FormalContext import FormalContext
# from LatticeParser import LatticeParser



if ( __name__ == "__main__"):
    attributes_filename = None
    objects_filename = None
    output_path = "."
    verbose = False

    parserFlag = False
    latticeInput = None
    latticeOutput = None

    options, remainder = getopt.getopt(sys.argv[1:], 'a:o:vhp',
                                       ['attributes_filename=', 'objects_filename=', '--output_path=','verbose', 'help', 'parser', 'lattice_input', 'lattice_output'])
    for opt, arg in options:
        if opt in ('-p', '--parser'):
            parserFlag = True

        elif opt in ('--lattice_input'):
            latticeInput = arg

        elif opt in ('--lattice_output'):
            latticeOutput = arg

        elif opt in ('-a', '--attributes_filename'):
            attributes_filename = arg

        elif opt in ('-o', '--objects_filename'):
            objects_filename = arg

        elif opt in ('--output_path'):
            output_path = arg

        elif opt in ('-v', '--verbose'):
            verbose = True

        elif opt in ('-h', '--help'):
            print "[HELP]"
            print "Try using: python %s  with the following parameters" % sys.argv[0]
            print "\tGenerating Formal Context"
            print "\t\t-a or --attributes_filename <attributes_filename>: required"
            print "\t\t-o or --objects_filename <objects_filename>: required"
            print "\n\tParsing lattice"
            print "\t\t--lattice_input <lattice_input>: required"
            print "\t\t--lattice_output <lattice_output>: required"
            print "\t\t--output_path <output_path>: optional"
            print "\n\tGeneral"
            print "\t\t-v or --verbose: optional"
            print "\t\t-h or --help: optional"
            sys.exit()


    startTime = time.time()

    if not parserFlag:
        print "[START]"
        fc = FormalContext(attributes_filename, objects_filename, output_path=output_path, verbose=True)
        fc.load_data()
        fc.build_formal_context()
        fc.exportToCoronSystem()
        print "\t... execution total time:", int(time.time() - startTime), "seconds"
        print "[DONE]"
    else:
        print "[START]"
        # parser = xml.sax.make_parser()
        # parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        #
        # Handler = LatticeParser(output_path)
        # parser.setContentHandler(Handler)
        #
        # parser.parse(latticeInput)
        # Handler.export_to_json(latticeOutput)

        print "\t... execution total time:", int(time.time() - startTime), "seconds"
        print "[DONE]"


    print "\t... execution total time:", int(time.time() - startTime), "seconds"
    print "[DONE]"
