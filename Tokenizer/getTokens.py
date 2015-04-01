import sys
import time

import langid
import nltk
from unidecode import unidecode
from nltk.corpus import stopwords
from Models import Publication, Token, Ocurrence
import BaseXClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func


def basex_result(result_str, separator='++++'):
    return result_str.split(separator)[0], result_str.split(separator)[1]


def is_valid_token(token):
    if len(token) >= 4 and token not in stopwords.words('english') and not any(c.isdigit() for c in token):
        return True
    else:
        return False


def save_publication(database, title, dblp_key, publication_type):
    qty = database.query(func.count(Publication.id)).filter(Publication.dblp_key == dblp_key).scalar()
    if qty == 0:
        publication = Publication(title=title, dblp_key=dblp_key, type=publication_type)
        database.add(publication)
        database.commit()
        return publication
    else:
        return database.query(Publication).filter_by(dblp_key=dblp_key).first()


def save_token(database, token):
    # qty = database.query(Token).filter_by(token=token).count()
    qty = database.query(func.count(Token.id)).filter(Token.token == token).scalar()
    if qty == 0:
        token = Token(token=token)
        database.add(token)
        database.commit()
        return token
    else:
        return database.query(Token).filter_by(token=token).first()


def save_ocurrence(database, token_instance, publication_instance):
    qty = database.query(func.count(Ocurrence.id)).filter(Ocurrence.token == token_instance, Ocurrence.publication == publication_instance).scalar()
    # qty = database.query(Ocurrence).filter_by(token=token_instance, publication=publication_instance).count()
    if qty == 0:
        ocurrence = Ocurrence(token=token_instance, publication=publication_instance)
        database.add(ocurrence)
        database.commit()
        return ocurrence
    else:
        return database.query(Ocurrence).filter_by(token=token_instance, publication=publication_instance)


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

try:
    Base = declarative_base()
    engine = create_engine("postgresql+psycopg2://khrno:@localhost/dblp_v2")
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    db = DBSession()
except SQLAlchemyError:
    print '[ERROR] SQLALchemy cant connect to database'
    sys.error()

# publication_types = ['proceedings', 'book','mastersthesis', 'phdthesis'] #[9, 6952]
publication_types = ['incollection']
tokens = []

qty_english = 0
for publication_type in publication_types:
    total_qty = int(conn.execute("XQUERY count(//%s)" % publication_type))
    print "Analysing %d documents of %s" % (total_qty, publication_type)

    results = conn.query("for $p in //%s return data($p/@key) || '++++' || $p//title" % publication_type)
    for itemtype, result in results.iter():
        dblp_key, title = basex_result(result)

        dblp_key = str(unidecode(dblp_key))
        title = str(unidecode(title))
        language = langid.classify(title)[0]

        if language == 'en':
            publicationObj = save_publication(db, title, dblp_key, publication_type)
            qty_english += 1
            for w in nltk.wordpunct_tokenize(title.lower()):
                if is_valid_token(w):
                    tokenObj = save_token(db, w)
                    save_ocurrence(db, tokenObj, publicationObj)
                    tokens.append(w)

tokens_unique = list(set(tokens))

print "%d tokens in %d documents in english found in %d seconds" % (len(tokens_unique), qty_english,
                                                                    int(time.clock() - start))




# bigram_measures = nltk.collocations.BigramAssocMeasures()
# finder = BigramCollocationFinder.from_words(tokens)
# ntop = int(len(tokens)*10/100)
# #
# print "\nraw_freq top %d" % ntop
# # print finder.nbest(bigram_measures.raw_freq, ntop)
#
# scored = finder.score_ngrams(bigram_measures.raw_freq)
# cont = 0
# for bigram, score in scored:
#     cont += 1
#     if cont % 50 == 0:
#         raw_input('You are viewing %d of %d bigrams.\nPlease press any key to continue...' % (cont, len(scored)))
#     print bigram, score
# #
#







