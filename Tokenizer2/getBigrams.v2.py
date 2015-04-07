import nltk
import time
import csv
from nltk.collocations import BigramCollocationFinder

inputTokenFilename = 'Data/token.txt.tmp'
minimalBigramFreq = 40
outputTokenFrequencyFilename = 'Data/output/token_frequency.csv'
outputBigramFrequencyFilename = 'Data/output/bigram_frequency.csv'
outputTokenFilename = 'Data/output/tokens.txt'
outputBigramFilename = 'Data/output/bigrams.txt'
outputTermsFilename = 'Data/output/terms.txt'

bigram_measures = nltk.collocations.BigramAssocMeasures()
tokens = []
with open(inputTokenFilename, 'r') as inputTokenFile:
    for line in inputTokenFile.readlines():
        token = line.rstrip('\n')
        tokens.append(token)

print "%d tokens loaded" % len(tokens)

start = time.time()
word_fd = nltk.FreqDist(tokens)
print "%d seconds in calculate word_fd" % int(time.time() - start)

start = time.time()
bigram_fd = nltk.FreqDist(nltk.bigrams(tokens))
print "%d seconds in calculate bigram_fd" % int(time.time() - start)

start = time.time()
finder = BigramCollocationFinder(word_fd, bigram_fd)
print "%d seconds in generate %d bigrams" % (int(time.time() - start), len(finder.ngram_fd.keys()))

start = time.time()
finder.apply_freq_filter(minimalBigramFreq)
print "%d bigrams filtered in %d seconds with minimal frequency of %d" % (len(finder.ngram_fd.keys()),
                                                                          int(time.time() - start),
                                                                          minimalBigramFreq)
start = time.time()
with open(outputTermsFilename, 'wb') as outputTermFile:
    tstart = time.time()
    termWriter = csv.writer(outputTermFile, delimiter=',')

    with open(outputTokenFrequencyFilename, 'wb') as outputTokenFrequencyFile:
        with open(outputTokenFilename, 'wb') as outputTokenFile:
            tokenFrequencyWriter = csv.writer(outputTokenFrequencyFile, delimiter=',')
            tokenWriter = csv.writer(outputTokenFile, delimiter=',')
            tokenFrequencyWriter.writerow(['token', 'frequency'])
            for token in finder.word_fd.keys():
                tokenFrequencyWriter.writerow([token, finder.word_fd[token]])
                tokenWriter.writerow([token])
                termWriter.writerow([token])
    print "%d tokens and their frequency writing in %s and %s in %d seconds" % (len(finder.word_fd.keys()),
                                                                                outputTokenFrequencyFilename,
                                                                                outputTokenFilename,
                                                                                int(time.time() - tstart))

    bstart = time.time()
    with open(outputBigramFrequencyFilename, 'wb') as outputBigramFrequencyFile:
        with open(outputBigramFilename, 'wb') as outputBigramFile:
            bigramFrequencyWriter = csv.writer(outputBigramFrequencyFile, delimiter=',')
            bigramWriter = csv.writer(outputBigramFile, delimiter=',')
            bigramFrequencyWriter.writerow(['bigram', 'frequency'])
            for bigram in finder.ngram_fd.keys():
                bigram_str = "%s_%s" % (bigram[0], bigram[1])
                bigramFrequencyWriter.writerow([bigram_str, finder.ngram_fd[bigram]])
                bigramWriter.writerow([bigram_str])
                termWriter.writerow([bigram_str])
    print "%d bigrams and their frequency writing in %s and %s in %d seconds" % (len(finder.ngram_fd.keys()),
                                                                                 outputBigramFrequencyFilename,
                                                                                 outputBigramFilename,
                                                                                 int(time.time() - bstart))

print "%d terms written in %s in %d seconds" % ((len(finder.word_fd.keys()) + len(finder.ngram_fd.keys())),
                                                outputTermsFilename,
                                                int(time.time() - start))
