#!/usr/bin/python

import xml.sax
import sys  
import codecs
from unidecode import unidecode



class DBLPHandler(xml.sax.ContentHandler):
    def __init__(self, output_path, verbose=False):
        self.CurrentData = ""
        self.title =  ""
        self.paperKey = ""
        self.article = {'year':'', 'title':''}
        self.verbose = verbose
        output_data = output_path + "/DBLP.csv"
        output_ids = output_path + "/MapIdsToDBLP.csv"
        self.cont = 0
        self.contTitles = 0
        self.file = codecs.open(output_data, "w", "iso-8859-1")
        self.fileIds = codecs.open(output_ids, "w", "iso-8859-1")
        self.fileTitles = codecs.open(output_path + "/titles.txt", "w", "iso-8859-1")

        
        firstLineData = "internal_id,year,title \n"
        self.file.write(firstLineData)

        firstLineFileIds = "internal_id,dblp_id \n"
        self.fileIds.write(firstLineFileIds)

    def startElement(self, tag, attributes):
        self.CurrentData = tag
        self.cont+=1
        if tag == "article":
            self.paperKey = attributes.get("key")

    def endElement(self, tag):
        if tag == "title":
            self.article['title'] = self.title
            self.fileTitles.write(unidecode("%s\n" % self.title))
            self.contTitles+=1
        if tag == "year":
            self.article['year'] = self.year
        

        if len(self.article['title']) > 0 and len(self.article['year']) > 0 and int(self.article['year']) >= 1970:
            data = unidecode("p" + str(self.cont) + "," + self.article['year'] + ',' + self.article['title'] + '\n')
            dataIds = unidecode("p" + str(self.cont) + "," + self.paperKey + '\n')
            self.file.write(data)
            self.fileIds.write(dataIds)
            if self.verbose and self.contTitles % 10000 == 0:
                print "%d) %s" %(self.contTitles, self.article['title'])
            self.article['title'] = ""
            self.article['year'] = ""

        elif self.CurrentData == "dblp":
            self.file.close()
            self.fileIds.close()
            self.fileTitles.close()
            if self.verbose:
                print "%d titles was written in %s" %(self.contTitles, self.output_path + "/titles.txt")
            sys.exit("stop")

    def characters(self, content):
        if self.CurrentData == "title":
            self.title = content.strip().rstrip('\n').replace('"','')
        elif self.CurrentData == "year":
            self.year = content.strip().rstrip('\n')






