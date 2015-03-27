import langid
import BaseXClient
import sys
import nltk
import string
import time
from unidecode import unidecode
from nltk.corpus import stopwords
from nltk.collocations import BigramCollocationFinder


def isValidToken(token):
	if len(token) >= 4 and token not in stopwords.words('english') and not any(c.isdigit() for c in token):
		return True
	else:
		return False

start = time.clock()

try:
	conn = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
	try:
		conn.execute("OPEN dblp")
	except IOError:
		print "[ERROR] database dblp does not exist"
		sys.exit()
except IOError:
	print "[ERROR] BaseX server is not running"
	sys.exit()

# publication_types = ['mastersthesis', 'phdthesis'] #[9, 6952]
publication_types = ['www']
tokens = []
for publication_type in publication_types:
	total_qty = int(conn.execute("XQUERY count(//%s)" % publication_type))
	print "Analysing %d documents of %s" % (total_qty, publication_type)

	results = conn.query("for $p in //%s return $p//title/text()" % publication_type)
	for itemtype,title in results.iter():
		title = str(unidecode(title))
		language = langid.classify(title)[0] 
		if language == 'en':
			for w in nltk.wordpunct_tokenize(title.lower()):
				if isValidToken(w):
					tokens.append(w)

tokens = list(set(tokens))

print "%d tokens found in %d seconds" % (len(tokens), int(time.clock() - start))


# bigram_measures = nltk.collocations.BigramAssocMeasures()
# finder = BigramCollocationFinder.from_words(tokens)
# scored = finder.score_ngrams(bigram_measures.raw_freq)
# # print sorted(bigram for bigram, score in scored)
# for bigram, score in scored:
# 	print bigram,score







