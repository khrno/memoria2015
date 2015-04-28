#!/usr/bin/python

import xml.sax
import sys
import codecs
import argparse
import ConfigParser
import time
from unidecode import unidecode

class DBLPHandler(xml.sax.ContentHandler):
    def __init__(self, csvFilename, verbose=False):
        self.CurrentData = ""
        self.title =  ""
        self.article = {'year':'', 'title':''}
        self.verbose = verbose
        self.file = codecs.open(csvFilename, "w", "iso-8859-1")

    def startElement(self, tag, attributes):
        self.CurrentData = tag

    def endElement(self, tag):
        if tag == "title":
            self.article['title'] = self.title.replace("'","").replace("\"","").replace("\n","").replace("\r","")
        if tag == "year":
            self.article['year'] = self.year

        if len(self.article['title']) > 0 and len(self.article['year']) > 0:
            data = unidecode(self.article['year'] + ',' + self.article['title'] + '\n')
            self.file.write(data)
            if self.verbose:
                print data
            self.article['title'] = ""
            self.article['year'] = ""
        elif self.CurrentData == "dblp":
            self.file.close()
            sys.exit("stop")

    # TODO: Delete quotes
    def characters(self, content):
        if self.CurrentData == "title":
            self.title = content.strip().rstrip('\n')
        elif self.CurrentData == "year":
            self.year = content.strip().rstrip('\n')

if ( __name__ == "__main__"):
    argParser = argparse.ArgumentParser(description="Parse dblp xml file and write the years and titles in csv format")
    
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
    csvfilename = Config.get(sys.argv[0][:-3], "csvfilename")

    print "[START]"
    print "Reading from %s" % xmlfilename
    print "Writing in %s" % csvfilename
    if args.timing:
        t0 = time.time()
    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = DBLPHandler(csvfilename, args.verbose)
    parser.setContentHandler(Handler)
    parser.parse(xmlfilename)
    if args.timing:
        t1 = time.time()
        print "Execution time: %0.3f seconds" % float(t1-t0)

    print "[END]"
