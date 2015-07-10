import xml.sax

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
			'id':-1,
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
			self.concept['id'] = int(attributes['id'])
		
		if 'empty' in attributes.keys():
			self.concept['empty'] = attributes['empty'] == "true"
		else:
			self.concept['empty'] = False
		if 'type' in attributes.keys():
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
			self.concept = {'id':-1, 'extent':[], 'intent':[], 'parents':[], 'children':[]}


		if self.verbose and tag == "lattice_stat":
			print "\t[DONE]"
		if self.verbose and tag == "objects":
			print "\t\t[DONE]"
		if self.verbose and tag == "attributes":
			print "\t\t[DONE]"
		if self.verbose and tag == "concepts":
			print "\t\t[DONE]"


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

