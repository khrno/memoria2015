import sys
import argparse
import ConfigParser
import time
import csv
from ParserLattice import Lattice

class JaccardSimilarity():
	def __init__(self, lattice, topictermsfilename, verbose = False):
		self.lattice = lattice
		self.verbose = verbose
		self.topics = []
		self.loadTopicTerms()

		self.similarityMap = self.calculateJaccardSimilarity()

	def jaccard(self, a, b):
		return float(len(set(a) & set(b))) / len(set(a) | set(b))

	def loadTopicTerms(self):
		with open(topictermsfilename, 'r') as topictermsfile:
			reader = csv.reader(topictermsfile, delimiter=",")
			header = reader.next()
			for row in reader:
				topic = row[0]
				words = row[1:]
				topicvocabulary = {'topic':topic, 'vocabulary':words}
				self.topics.append(topicvocabulary)
		if self.verbose:
			print "\t%d topics loaded" % len(self.topics)

	def calculateJaccardSimilarity(self):
		similarityMap = {}
		if self.verbose:
			print "\t calculate jaccard similarity"
		for topic in self.topics:
			for concept in self.lattice.concepts:
				if concept["type"] == "inner":
					intentAttr = []
					for attrId in concept["intent"]:
						intentAttr.append(self.lattice.getAttributeById(attrId))
					simKey = (topic["topic"], concept["id"])
					simValue = self.jaccard(topic["vocabulary"],intentAttr)
					similarityMap[simKey] = simValue
		return similarityMap

	def exportSimilarities(self, outputfilename, outputPath=None):
		if self.verbose:
			print "\tExporting similarities"
		
		logfilename = outputfilename.split(".csv")[0] + ".log"
		''' Writing stats file '''
		if self.verbose:
			print "\t\tExporting stats"
		with open(logfilename, "w") as logFile:
			''' Writing lattice stats in log file '''
			logFile.write("Lattice Stats\n")
			for k in self.lattice.stats.keys():
				logFile.write("%s = %s\n" %(k, str(self.lattice.stats[k])))
			''' Writing topic stats in log file '''
			logFile.write("\nTopics Stats\n")
			for topic in self.topics:
				logFile.write("%s: %d terms\n" % (topic['topic'], len(topic['vocabulary'])))
		
		if outputPath == None:
			outputPath = "%s/sims/" % "/".join(outputfilename.split("/")[:-1])

		if self.verbose:
			print "\t\tExporting values..."
		with open(outputfilename, "w") as outputFile:
			writer = csv.writer(outputFile, delimiter=",")
			header = ["topic_name", "concept_id", "jaccard_simmilarity"]
			writer.writerow(header)
			for concept in self.lattice.concepts:
				if concept["type"]=="inner":
					simConceptFilename = "%ssims_%d.csv" % (outputPath,int(concept["id"]))
					with open(simConceptFilename, "w") as simConceptFile:
						writerConceptFile = csv.writer(simConceptFile, delimiter=",")
						writerConceptFile.writerow(["topic_name","jaccard_simmilarity"])
						for topic in self.topics:
							simValue = self.similarityMap[(topic["topic"],concept["id"])]
							writerConceptFile.writerow([topic["topic"],simValue])
							writer.writerow([topic["topic"],concept["id"],simValue])





	def calculateJaccardSimilarityBetweenIntentAndTopics(self, outputfilename):
		print "[WARNING] calculateJaccardSimilarityBetweenIntentAndTopics was deprecated"
		''' DEPRECATED '''
		logfilename = outputfilename.split(".csv")[0] + ".log"
		''' Writing lattice stats in log file '''
		with open(logfilename, "w") as logFile:
			logFile.write("Lattice Stats\n")
			for k in self.lattice.stats.keys():
				logFile.write("%s = %s\n" %(k, str(self.lattice.stats[k])))

			logFile.write("\nTopics Stats\n")
			for topic in self.topics:
				logFile.write("%s: %d terms\n" % (topic['topic'], len(topic['vocabulary'])))


		with open(outputfilename, "w") as outputFile:
			writer = csv.writer(outputFile, delimiter=",")
			header = ["topic_name", "concept_id", "jaccard_simmilarity"]
			writer.writerow(header)
			for topic in self.topics:
				for concept in self.lattice.concepts:
					if concept['type'] == "inner":
						intentAttr = []
						for attrId in concept['intent']:
							intentAttr.append(self.lattice.getAttributeById(attrId))
						row = [topic['topic'], concept['id'], self.jaccard(topic['vocabulary'],intentAttr)]
						if self.verbose:
							print "%s,%s,%f" % (topic['topic'],concept['id'],self.jaccard(topic['vocabulary'],intentAttr))
						writer.writerow(row)



if ( __name__ == "__main__"):
    argParser = argparse.ArgumentParser(description="Calculate jaccard similarity between topics and formal concepts")
    
    argParser.add_argument("-v", "--verbose", action="store_true", 
        help="display each line to write in the csv file")
    argParser.add_argument("-t", "--timing", action="store_true",
        help="display the time of execution")
    argParser.add_argument("-c", "--config", type=str, required=True, 
        help="filepath to configuration file to read")
    args = argParser.parse_args()
    Config = ConfigParser.ConfigParser()
    Config.read(args.config)
    
    topictermsfilename = Config.get(sys.argv[0][:-3], "topictermsfilename")
    latticefilename = Config.get(sys.argv[0][:-3], "latticefilename")
    topicconceptsimilarityfilename = Config.get(sys.argv[0][:-3], "topicconceptsimilarityfilename")
    tokenspath = Config.get(sys.argv[0][:-3], "tokenspath")

    print "[START]"
    print "Parameter topictermsfilename %s" % topictermsfilename
    print "Parameter latticefilename %s" % latticefilename 
    print "Parameter topicconceptsimilarityfilename %s" % topicconceptsimilarityfilename
    print "Parameter tokenspath %s" % tokenspath
    
    

    if args.timing:
        t0 = time.time()

    lattice = Lattice(latticefilename, intentExtended=True, tokensPath = tokenspath,verbose=args.verbose)
    jaccard = JaccardSimilarity(lattice, topictermsfilename, args.verbose)
    jaccard.exportSimilarities(topicconceptsimilarityfilename)

    if args.timing:
        t1 = time.time()
        print "Execution time: %0.3f seconds" % float(t1-t0)

    print "[END]"