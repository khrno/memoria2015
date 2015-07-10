#!/usr/bin/python

import xml.sax
import sys
import argparse
import ConfigParser
import time
import os
import csv
import gexf
from os.path import isfile,join
from LatticeHandler import LatticeHandler

class Lattice():

	def __init__(self, latticefilename, intentExtended=False, tokensPath = None, similarityPath=None, verbose = False):
		'''Parser the lattice file'''
		parser = xml.sax.make_parser()
		parser.setFeature(xml.sax.handler.feature_namespaces, 0)
		parser.setFeature(xml.sax.handler.feature_external_ges, False)
		Handler = LatticeHandler(verbose)
		parser.setContentHandler(Handler)
		parser.parse(latticefilename)

		self.latticefilename = latticefilename
		self.attributes = Handler.attributes
		self.objects = Handler.objects
		self.concepts = Handler.concepts
		self.stats = Handler.stats
		self.verbose = verbose

		self.intentExtended = False

		self.getMaxLevel()
		
		self.oobjects = self.optimizeObjects()

		if intentExtended:
			self.extendIntent(tokensPath)

		if similarityPath:
			self.loadSimilarities(similarityPath)
		
	def loadSimilarities(self, similarityPath):
		if self.verbose:
			print "\tReading similarities from..."
		for concept in self.concepts:
			similarities = []
			if concept["type"] == "inner":
				similarityFilename = "%s" % join(similarityPath,"sims_%d.csv" % int(concept["id"]))
				if isfile(similarityFilename):
					with open(similarityFilename, "r") as simFile:
						reader = csv.reader(simFile, delimiter=",")
						header = reader.next()
						for row in reader:
							topic_name,similarity_value = row[0], row[1]
							t = (similarity_value, topic_name)
							similarities.append(t)
				else:
					concept["topic_distribution"] = []
				similarities.sort(reverse=True)
				concept["topic_distribution"] = similarities
			else:
				concept["topic_distribution"] = []
		if self.verbose:
			print "\t[DONE]"



	def optimizeObjects(self):
		if self.verbose:
			print "\tOptmizing objects...",
		mapObj = {}
		for obj in self.objects:
			mapObj[int(obj['id'])] = obj['obj']
		if self.verbose:
			print "\t\t[DONE]"
		return mapObj

	def getConceptById(self, lookup):
		for concept in self.concepts:
			if int(concept["id"]) == int(lookup):
				return concept
		return None

	def getAttributeExtendedId(self, attributesExtended, token):
		maxid = 0
		for attr in attributesExtended:
			if int(attr["id"]) > maxid:
				maxid = int(attr["id"])
			if attr["attr"] == token:
				return attr["id"]
		maxid = maxid + 1
		attributesExtended.append({"id":str(maxid), "attr": token})
		return str(maxid)

	def extendIntent(self, tokensPath):
		print "\tExtending intent...",
		attributesExtended = []
		for concept in self.concepts:
			if concept["type"] == "inner":
				tokenFilename = join(tokensPath, "t_%d.txt" % int(concept["id"]))
				intentExtended = []
				with open(tokenFilename, "r") as tokenFile:
					for line in tokenFile:
						token = line.rsplit("\n")[0]
						tokenId = self.getAttributeExtendedId(attributesExtended, token)
						intentExtended.append(tokenId)
				concept["intentExtended"] = intentExtended
				concept["intentBase"] = concept["intent"]

				concept["intent"] = concept["intentExtended"]
			else:
				concept["intentExtended"] = None
				concept["intentBase"] = concept["intent"]
		self.attributesExtended = attributesExtended
		self.attributesBase = self.attributes
		self.intentExtended = True
		self.attributes = self.attributesExtended
		
		if self.verbose:
			print "\t\t[DONE]"

	def getMaxLevel(self):
		self.stats['max_level'] = -1
		for c in self.concepts:
			if c['level'] > self.stats['max_level']:
				self.stats['max_level'] = c['level']

	def getAttributeById(self, lookup):
		if self.intentExtended:
			return self.getAttributeExtendedById(lookup)
		else:
			return self.getAttributeBaseById(lookup)

	def getAttributeBaseById(self, lookup):
		for attr in self.attributes:
			if attr['id'] == lookup:
				return attr['attr']
		return None

	def getAttributeExtendedById(self, lookup):
		for attr in self.attributesExtended:
			if attr['id'] == lookup:
				return attr['attr']
		return None	

	def getObjectById(self, lookup):
		print "[WARNING] using unoptimized look for object in lattice."
		for obj in self.objects:
			if obj['id'] == lookup:
				return obj['obj']

	def getoObjectById(self, lookup):
		obj = None
		if lookup and len(lookup)>0:
			# if int(lookup) in self.oobjects.keys():
			try:
				obj = self.oobjects[int(lookup)]
			except KeyError:
				print "[WARNING] object id %d dont found" % int(lookup)
				obj = None
			# else:
				# return None
		else:
			obj = None
		return obj

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

	def getTopKAttributesByConcept(self, k, concept):
		attributes = []
		for i in range(0,min(k,len(concept["intent"]))):
			attrId = concept["intent"][i]
			attributes.append(self.getAttributeById(attrId))
		return attributes

	def getTopKTopicSimilarityByConcept(self, k, concept):
		return concept["topic_distribution"][:k] if "topic_distribution" in concept.keys() else []

	def getConceptsByLevel(self, level, sort=False):
		conceptsByLevel = []
		for concept in self.concepts:
			if int(concept["level"]) == int(level):
				conceptsByLevel.append(concept)
		if sort:
			conceptsByLevel.sort(key=lambda x: int(x["supp_abs"]), reverse=True)

		return conceptsByLevel




	def exportLatticeToGEXFFormat(self, outputFilename, topK=5, description=None):
		if description == None:
			description = "GEXF file from lattice %s" % self.latticefilename
		
		gexfFormat = gexf.Gexf("Pablo Ortega Mesa", description)
		graph = gexfFormat.addGraph("directed","static",description)

		# Node attributes
		attributeConceptId = graph.addNodeAttribute("ConceptID","0",type="integer")
		attributeLevelId = graph.addNodeAttribute("Level","-1",type="integer")
		attributeTypeId = graph.addNodeAttribute("Type","",type="string")
		attributeSuppId = graph.addNodeAttribute("Support","0", type="integer")
		attributeURIId = graph.addNodeAttribute("URI","",type="string")

		attributeTopIntentId = graph.addNodeAttribute("TopIntent","",type="string")
		attributeTopSimilarityId = graph.addNodeAttribute("TopSimilarity","",type="string")

		for concept in self.concepts:
			label = "concept-"+str(concept["id"])
			node = graph.addNode(concept["id"],label)

			# Node Attributes Values
			node.addAttribute(id=attributeConceptId, value=str(concept["id"]))
			node.addAttribute(id=attributeLevelId, value=str(concept["level"]))
			node.addAttribute(id=attributeTypeId, value=concept["type"])
			if "supp_abs" in concept.keys() and isinstance(concept["supp_abs"], (int,str)):
				node.addAttribute(id=attributeSuppId, value=str(concept["supp_abs"]))

			node.addAttribute(id=attributeURIId, value="/c%d" % concept["id"])

			node.addAttribute(id=attributeTopIntentId, value=",".join(self.getTopKAttributesByConcept(topK,concept)))

			'''topic distribution string line'''
			topic_distribution = []
			for t in self.getTopKTopicSimilarityByConcept(topK,concept):
				topic_distribution.append(t[1])				
			node.addAttribute(id=attributeTopSimilarityId, value=",".join(topic_distribution))

		i=0
		for concept in self.concepts:
			for child in concept["children"]:
				graph.addEdge(str(i),concept["id"],int(child))
				i+=1
		with open(outputFilename,"w") as outputFile:
			gexfFormat.write(outputFile)





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
