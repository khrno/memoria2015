import csv
import time
import logging
import os
import os.path

import langid
import nltk
from nltk.corpus import stopwords

start = time.time()

print "[START]"


def is_valid_token(token):
    tagged = dict(nltk.pos_tag([token]))
    if len(token) >= 4:
        if token not in stopwords.words('english'):
            if not any(c.isdigit() for c in token):
                if tagged[token].startswith('N'):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False


def load_tokens(filename):
    ltokens = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as tokenFile:
            datareader = csv.reader(tokenFile, delimiter=',')
            for row in datareader:
                ltokens.append(row[0])
        print "\t%d token loaded from %s" % (len(ltokens), filename)
    return ltokens


def save_tokens(filename, tokens):
    with open(filename, 'w') as tokenFile:
        for token in tokens:
            tokenFile.write("%s\n" % token)


filename = 'Data/dblp.csv'
tokenFilename = 'Data/token.txt.tmp'
logFilename = "getTokens.runtime"
logging.basicConfig(filename=logFilename, level=logging.DEBUG)

Nlimit = 200000
tokens = load_tokens(tokenFilename)
publicationCounter = 0
publicationEnglishCounter = 0

with open(filename, 'rb') as csvfile:
    print "\n"
    datareader = csv.reader(csvfile, delimiter=',')
    for row in datareader:
        title = row[1]
        publicationCounter += 1
        if langid.classify(title)[0] == 'en':
            publicationEnglishCounter += 1
            for w in nltk.wordpunct_tokenize(title.lower()):
                if is_valid_token(w):
                    tokens.append(w)
            if publicationEnglishCounter % 1000 == 0:
                print "\tStill alive... %d publications processed" % publicationCounter
                logging.debug("Still alive... %d publications processed" % publicationCounter)
            if publicationEnglishCounter == Nlimit:
                break
    print "\n"

save_tokens(tokenFilename, tokens)

qty_tokens = len(tokens)
tokens = list(set(tokens))

os.system("sed '1,%dd' %s > %s.tmp; mv %s.tmp %s" % (publicationCounter, filename, filename, filename, filename))

logging.info('N limit: %d' % Nlimit)
logging.info("Unique tokens: %d" % len(tokens))
logging.info("Total tokens: %d" % qty_tokens)
logging.info("Token filename: %s" % tokenFilename)
logging.info("Publication filename: %s" % filename)
logging.info("Total publications: %d" % publicationCounter)
logging.info("English publications: %d" % publicationEnglishCounter)
logging.info("Total execution time %d seconds\n" % int(time.time() - start))

print "\tN limit: %d" % Nlimit
print "\tUnique tokens: %d" % len(tokens)
print "\tTotal tokens: %d" % qty_tokens
print "\tToken filename: %s" % tokenFilename
print "\tPublication filename: %s" % filename
print "\tTotal publications: %d" % publicationCounter
print "\tEnglish publications: %d" % publicationEnglishCounter
print "\n\tTotal execution time %d seconds" % int(time.time() - start)
print "[DONE]"
