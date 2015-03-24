#!/usr/bin/python

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

    def export_to_json(self, json_filename):
        with open(json_filename, "w") as outputFile:
            outputFile.write(json.dumps(self.lattice))

    def test(self,filename):
        nodes = []
        nodesMapping = {} # {conceptId: nodeId}
        links = []

        for concept in self.lattice:
            nodes.append({'name': concept['id'], 'group': int(concept['level'])})

        for k in range(0, len(nodes)):
            nodesMapping[int(nodes[k]['name'])] = k


        for concept in self.lattice:
            for parent in concept['parents']:
                # print parent
                # print "{'source': %d, 'target': %d, 'value': 2})" % (nodesMapping[int(parent)], nodesMapping[int(concept['id'])])
                links.append({'source': nodesMapping[int(parent)],'target':nodesMapping[int(concept['id'])], 'value': 2})

        with open(filename, "w") as dataFile:
            dataFile.write(json.dumps({'nodes': nodes, 'links': links}))
        print "DUMPED"



parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces, 0)
Handler = LatticeParser()
parser.setContentHandler(Handler)
parser.parse("lattices/lattice.min100.xml")
Handler.test('lattice.min100.d3.json')
Handler.export_to_json('lattice.min100.json')