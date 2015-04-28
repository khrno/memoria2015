#!/usr/bin/python

import xml.sax
import sys
import argparse
import ConfigParser
import time

class Lattice():
	def __init__(self, attributes, objects, concepts, stats, verbose=False):
		self.attributes = attributes
		self.objects = objects
		self.concepts = concepts
		self.stats = stats
		self.verbose = verbose

		self.getMaxLevel()

	def getMaxLevel(self):
		self.stats['max_level'] = -1
		for c in self.concepts:
			if c['level'] > self.stats['max_level']:
				self.stats['max_level'] = c['level']

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

class LatticeHandler(xml.sax.ContentHandler):
	def __init__(self, verbose = False):
		self.verbose =  verbose
		self.CurrentData = ""
		self.attributes = []
		self.attribute = {'id': '', 'attr':''}
		self.objects = []
		self.object = {'id':'','obj':''}
		self.concepts = []
		self.concept = {
			'extent':[], 
			'intent':[], 
			'parents':[], 
			'children':[], 
			'supp_abs':-1, 
			'level':-1, 
			'empty':True, 
			'type':''
		}
		self.stats = {
			'largest_attr': -1,
			'nb_attr_avg': 0.0,
			'density': 0.0,
			'min_supp_abs': -1,
			'min_supp_rel': 0.0,
			'alg': '',
			'nb_inner_nodes': 0
		}

        def startElement(self, tag, attributes):
        	self.CurrentData = tag

        	if self.CurrentData == "obj":
        		self.object['id'] = attributes['id']

        	if self.CurrentData == "attr":
        		self.attribute['id'] = attributes['id']

        	if self.CurrentData == "concept":
        		self.concept['supp_abs'] = int(attributes["supp_abs"])
        		self.concept['level'] = int(attributes["level"])
        		if 'empty' in attributes.keys():
        			self.concept['empty'] = attributes['empty'] == "true"
        		else:
        			self.concept['empty'] = False
        		self.concept['type'] = attributes['type']
        	
        	if self.verbose and self.CurrentData == "db_stat":
        		print "\tReading lattice stats...",
        	
        	if self.verbose and self.CurrentData == "objects":
        		print "\tReading objects...",

        	if self.verbose and self.CurrentData == "attributes":
        		print "\tReading attributes...",

        	if self.verbose and self.CurrentData == "concepts":
        		print "\tReading concepts...",

        	


        def endElement(self, tag):
        	if tag == "obj":
	    		self.objects.append(self.object)
	    		self.object = {'id':'','obj':''}

	    	if tag == "attr":
	    		self.attributes.append(self.attribute)
	    		self.attribute = {'id': '', 'attr':''}

	    	if tag == "concept":
	    		self.concepts.append(self.concept)
	    		self.concept = {'extent':[], 'intent':[], 'parents':[], 'children':[]}


        	if self.verbose and tag == "lattice_stat":
	    		print "\t[DONE]"
	    	if self.verbose and tag == "objects":
	    		print "\t\t[DONE]"
	    	if self.verbose and tag == "attributes":
	    		print "\t\t[DONE]"
	    	if self.verbose and tag == "concepts":
	    		print "\t\t[DONE]\n"

	    	# if self.verbose and tag=="lattice":
	    	# 	print "\n"
	    	# 	print self.stats
	    	# 	print self.objects
	    	# 	print self.attributes
	    	# 	print len(self.concepts)
	    	# 	print "\n"
	    	



        def characters(self, content):
        	'''Reading stats'''
        	if self.CurrentData == "largest_attr":
        		self.stats['largest_attr'] = int(content.strip().rstrip('\n'))
        	elif self.CurrentData == "nb_attr_avg":
        		self.stats['nb_attr_avg'] = float(content.strip().rstrip('\n').replace(",",".").replace("%",""))
        	elif self.CurrentData == "density":
        		self.stats['density'] = float(content.strip().rstrip('\n').replace(",",".").replace("%",""))
        	elif self.CurrentData == "min_supp_abs":
        		self.stats['min_supp_abs'] = int(content.strip().rstrip('\n'))
        	elif self.CurrentData == "min_supp_rel":
        		self.stats['min_supp_rel'] = float(content.strip().rstrip('\n').replace(",",".").replace("%",""))
        	elif self.CurrentData == "alg":
        		self.stats['alg'] = content.strip().rstrip('\n')
        	elif self.CurrentData == "nb_inner_nodes":
        		self.stats['nb_inner_nodes'] = int(content.strip().rstrip('\n'))

        	'''Reading objects'''
        	if self.CurrentData == "obj":
        		self.object['obj'] = content.strip().rstrip('\n')

        	'''Reading attributes'''
        	if self.CurrentData == "attr":
        		self.attribute['attr'] = content.strip().rstrip('\n')

        	'''Reading concepts'''
        	if self.CurrentData == "extent" and len(content.strip()) > 0:
        		self.concept['extent'] = content.strip().rstrip('\n').split(",")
        	elif self.CurrentData == "intent" and len(content.strip()) > 0:
        		self.concept['intent'] = content.strip().rstrip('\n').split(",")
        	elif self.CurrentData == "parents" and len(content.strip()) > 0:
        		self.concept['parents'] = content.strip().rstrip('\n').split(",")
        	elif self.CurrentData == "children" and len(content.strip()) > 0:
        		self.concept['children'] = content.strip().rstrip('\n').split(",")




        # self.file = codecs.open(csvFilename, "w", "iso-8859-1")



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


	parser = xml.sax.make_parser()
	parser.setFeature(xml.sax.handler.feature_namespaces, 0)
	parser.setFeature(xml.sax.handler.feature_external_ges, False)
	Handler = LatticeHandler(args.verbose)
	parser.setContentHandler(Handler)
	parser.parse(xmlfilename)

	latt = Lattice(
		attributes=Handler.attributes,
		objects=Handler.objects,
		concepts=Handler.concepts,
		stats=Handler.stats,
		verbose=args.verbose)

	statsfilename = xmlfilename.split(".xml")[0] + ".stats.txt"

	latt.getLatticeStats(statsfilename)

    if args.timing:
        t1 = time.time()
        print "Execution time: %0.3f seconds" % float(t1-t0)

    print "[END]"
