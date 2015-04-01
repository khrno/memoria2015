import time

import langid

import BaseXClient


start = time.clock()
print "[START]"

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

publication_types = ['inproceedings']
en_qty = 0
for publication_type in publication_types:
    total_qty = int(conn.execute("XQUERY count(//%s)" % publication_type))
    results = conn.query("for $p in //%s return $p//title/text()" % publication_type)
    for itemtype, title in results.iter():
        language = langid.classify(title)[0]
        if language == 'en':
            en_qty += 1
    print "%d of %d are publications of type %s in english" % (en_qty, total_qty, publication_type)

print "[DONE] execution time: %d seconds" % int(time.clock() - start)