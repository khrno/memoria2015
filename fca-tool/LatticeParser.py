#!/usr/bin/python

import getopt
import sys
import xml.sax
import json


class LatticeParser(xml.sax.ContentHandler):
    def __init__(self):
        self.currentTag = ""
        self.concept = {
            'id': -1,
            'level': -1,
            'type': "",
            'intent': [],
            'extent': [],
            'parents': []
        }
        self.lattice = []
        self.attributes = {}
        self.objects = {}
        #iterators
        self.attrID = -1
        self.attrValue = ""
        self.objID = -1
        self.objValue = ""
        self.conceptId = -1
        self.conceptLevel = -1
        self.conceptType = ""
        self.intent = []
        self.extent = []
        self.parents = []

    def startElement(self, tag, attributes):
        self.currentTag = tag
        if self.currentTag == "obj":
            self.objID = attributes.get("id")
            self.objValue = ""

        if self.currentTag == "attr":
            self.attrID = attributes.get("id")
            self.attrValue = ""

        if self.currentTag == "concept":
            self.conceptId = attributes.get("id")
            self.conceptLevel = attributes.get("level")
            self.conceptType = attributes.get("type")

        if self.currentTag == "extent":
            self.extent = []

        if self.currentTag == "intent":
            self.intent = []

        if self.currentTag == "parents":
            self.parents = []


    def endElement(self, tag):
        # self.currentTag = ""
        if tag == "obj":
            self.objects[self.objID] = self.objValue

        if tag == "attr":
            self.attributes[self.attrID] = self.attrValue

        if tag == "concept":
            self.concept = {
                'id': self.conceptId,
                'level': self.conceptLevel,
                'type': self.conceptType,
                'intent': self.intent,
                'extent': self.extent,
                'parents': self.parents
            }
            self.lattice.append(self.concept)
            # print self.concept

        if tag == "concepts":
            print "DONE"


    def characters(self, content):
        value = content.strip().rstrip('\n').replace('"', '')

        if self.currentTag == "obj":
            self.objValue = value

        if self.currentTag == "attr":
            self.attrValue = value

        if self.currentTag == "extent":
            self.extent = value.split(",")

        if self.currentTag == "intent":
            self.intent = value.split(",")

        if self.currentTag == "parents":
            self.parents = value.split(",")

    def export(self, format, filename):
        if format == "d3":
            self.exportToD3(filename)
        if format == "json":
            self.export_to_json(filename)

    def export_to_json(self, json_filename):
        with open(json_filename, "w") as outputFile:
            outputFile.write(json.dumps(self.lattice))
        print "Exported to json"

    def exportToD3(self, filename):
        nodes = []
        nodesMapping = {} # {conceptId: nodeId}
        links = []

        for concept in self.lattice:
            nodes.append({'name': concept['id'], 'group': int(concept['level'])})

        for k in range(0, len(nodes)):
            nodesMapping[int(nodes[k]['name'])] = k


        for concept in self.lattice:
            for parent in concept['parents']:
                print parent
                if parent != '':
                # print "{'source': %d, 'target': %d, 'value': 2})" % (nodesMapping[int(parent)], nodesMapping[int(concept['id'])])
                    links.append({'source': nodesMapping[int(parent)],'target':nodesMapping[int(concept['id'])], 'value': 2})

        with open(filename, "w") as dataFile:
            dataFile.write(json.dumps({'nodes': nodes, 'links': links}))
        print "Exported to D3"




if ( __name__ == "__main__"):
    latticeInput = None
    latticeOutput = None
    formatTarget = "json"


    options, remainder = getopt.getopt(sys.argv[1:], 'i:o:f:h',
                                       ['lattice_input=', 'lattice_output=', 'format=', 'help'])
    for opt, arg in options:
        if opt in ('-i', '--lattice_input'):
            latticeInput = arg

        elif opt in ('-o', '--lattice_output'):
            latticeOutput = arg

        elif opt in ('-f', '--format'):
            formatTarget = True

        elif opt in ('-h', '--help'):
            print "[HELP]"
            print "Try using: python %s  with the following parameters" % sys.argv[0]
            print "\t-i or --lattice_input <lattice_input>: required"
            print "\t-o or --lattice_output <lattice_output>: required"
            print "\t-f or --format <format>: optional by default json"
            print "\t-h or --help: optional"
            sys.exit()

    parser = xml.sax.make_parser()
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    Handler = LatticeParser()
    parser.setContentHandler(Handler)
    parser.parse(latticeInput)
    Handler.exportToD3(latticeOutput)