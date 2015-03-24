#!/usr/bin/python

import time
import csv
import codecs
import numpy as np


class FormalContext:
    def __init__(self, attributes_filename, objects_filename, output_path=".", verbose=False):
        # params
        self.attributesFilename = attributes_filename
        self.objectsFilename = objects_filename
        self.outputPath = output_path
        self.verbose = verbose
        # class-defined
        self.attributes = []
        self.objects = []
        self.attributesLabel = {}
        self.objectsLabel = {}

        self.formalContext = None
        self.formalContextMatrix = None

    def load_data(self):
        startTime = time.time()
        with open(self.attributesFilename) as attributesFile:
            for attr in attributesFile.readlines():
                attr = attr.rstrip()
                self.attributes.append(attr)

        if self.verbose:
            print "\t... load %d tokens from %s in %d seconds" % (len(self.attributes), self.attributesFilename, int(time.time() - startTime))

        with open(self.objectsFilename) as objectsFile:
            rows = csv.DictReader(objectsFile)
            for row in rows:
                self.objects.append(row['title '])
                if row['title '] in self.objectsLabel.keys():
                    self.objectsLabel[row['title '] + "-2"] = row['internal_id']
                self.objectsLabel[row['title ']] = row['internal_id']

        if self.verbose:
            print "\t... load %d documents from %s in %d seconds" % (len(self.objects), self.objectsFilename, int(time.time() - startTime))

    def build_formal_context(self):
        startTime = time.time()
        print "\t... Staring calculate formal context... this can take several minutes.... please wait"
        ocurrences_row = []
        self.formalContext = []
        for attr in self.attributes:
            for obj in self.objects:
                if attr in obj.lower():
                    ocurrences_row.append('1')
                else:
                    ocurrences_row.append('0')

            self.formalContext.append(ocurrences_row)
            ocurrences_row = []

        self.formalContextMatrix = np.array(self.formalContext)
        if self.verbose:
            print "\t... formal context generated in %d seconds" % (int(time.time() - startTime))

    def exportToCoronSystem(self, latticeName="Default", latticeFilename="coron_contexts/formal_context.rcf"):
        startTime = time.time()
        formalContextMatrixT = self.formalContextMatrix.transpose()
        with codecs.open(latticeFilename, "w", "iso-8859-1") as formalContextFile:
            documentsLine = " | ".join(self.objectsLabel.values())
            tokensLine = " | ".join(self.attributes)

            formalContextFile.write("[Relational Context]\n")
            formalContextFile.write("%s\n" % (latticeName))
            formalContextFile.write("[Binary Relation]\n")
            formalContextFile.write("Name_of_dataset\n")
            formalContextFile.write("%s\n" % (documentsLine))
            formalContextFile.write("%s\n" % (tokensLine))
            for lineData in formalContextMatrixT:
                ocurrencesLine = " ".join(lineData)
                formalContextFile.write("%s\n" %(ocurrencesLine))
            formalContextFile.write("[END Relational Context]\n")

        if self.verbose:
            print "\t... lattice (%d x %d) %s write in %s in %s seconds" % (formalContextMatrixT.shape[0], formalContextMatrixT.shape[1], latticeName, latticeFilename, int(time.time() - startTime))


# startTime = time.time()
# fc = FormalContext('data/minimal/tokens.min100.txt', 'data/minimal/DBLP.min100.csv', verbose=True)
# print "[START]"
# fc.load_data()
# fc.build_formal_context()
# fc.exportToCoronSystem()
# print "\t... execution total time:", int(time.time() - startTime), "seconds"
# print "[DONE]"
