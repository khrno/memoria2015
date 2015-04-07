import time
import nltk
from nltk.collocations import BigramCollocationFinder


# Configurate parameteres
inputFilename = "Data/token.txt.tmp"
outputTokenFilename = "Data/tokens.txt"
outputBigramFilename = "Data/bigrams.txt"
bigram_min_freq = 15                                                # bigrams appear together in at least 15 documents


# Load Tokens NOT uniques
start = time.time()
tokens = []
with open(inputFilename, 'r') as inputFile:
    for line in inputFile.readlines():
        line = line.rstrip('\n')
        tokens.append(line)
print "%d tokens loaded from %s in %d seconds" % (len(tokens), inputFilename, int(time.time() - start))


# Generating unique tokens and writing them into outputTokenFilename
start = time.time()
unique_tokens = list(set(list(tokens)))
with open(outputTokenFilename, 'w') as outputTokenFile:
    for token in unique_tokens:
        outputTokenFile.write("%s\n" % token)
print "%d unique tokens written in %s in %d seconds" % (len(unique_tokens), outputTokenFilename,
                                                        int(time.time() - start))

# Generating bigrams
start = time.time()
bigram_measures = nltk.collocations.BigramAssocMeasures()
finder = BigramCollocationFinder.from_words(tokens)
bigrams = list(finder.nbest(bigram_measures.raw_freq, bigram_min_freq))
print "%d bigrams generated with minimal freq of %d in %d seconds" % (len(bigrams), bigram_min_freq,
                                                                      int(time.time() - start))

# Exporting bigrams
start = time.time()
with open(outputBigramFilename, 'w') as outputBigramFile:
    for bigram in bigrams:
        outputBigramFile.write("%s_%s\n" % (bigram[0], bigram[1]))
print "%d bigrams written in %s in %d seconds" % (len(bigrams), outputBigramFilename, int(time.time()-start))