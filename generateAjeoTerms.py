import csv

inputFilename = "ajeo.topicterms.csv"

terms = []
with open(inputFilename, 'r') as inputFilename:
	reader = csv.reader(inputFilename, delimiter=',')
	#Reading header
	qty = 0
	for row in reader:
		qty+=1
		if qty > 1:
			for word in row[1].split(" "):
				terms.append(word)

terms = list(set(terms))

print "load %d terms" % len(terms)

outputFilename = "ajeoterms.txt"
with open(outputFilename, 'w') as outputFilename:
	for term in terms:
		outputFilename.write(term+'\n')
