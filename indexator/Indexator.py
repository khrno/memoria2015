#!/usr/bin/python

import sys
import xml.dom.minidom
import time
from Libraries import BaseXClient
from unidecode import unidecode

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from models import TypeOfPublication, Person, Journal, Publication, PersonPublication

'''
newTypeOfPublication = TypeOfPublication(name="article")
session.add(newTypeOfPublication)
session.commit()
'''


class Indexator:
    def __init__(self, database_name, dbengine, verbose=False):
        self.database_name = database_name
        self.verbose = verbose
        self.conn = None
        self._types = ['article', 'inproceedings', 'proceedings', 'book', 'incollection', 'phdthesis', 'mastersthesis',
                       'www']
        self.session = self.createDBSession(dbengine)

        try:
            conn = BaseXClient.Session('localhost', 1984, 'admin', 'admin')
            try:
                conn.execute("OPEN " + self.database_name)
            except IOError:
                print "[ERROR] database %s does not exist" % self.database_name
                sys.exit()
        except IOError:
            print "[ERROR] BaseX server is not running"
            sys.exit()

        self.conn = conn

    def createDBSession(self, dbengine):
        Base = declarative_base()
        engine = create_engine(dbengine)
        Base.metadata.bind = engine

        DBSession = sessionmaker(bind=engine)
        return DBSession()


    def indexPublicationType(self, name):
        qty = self.session.query(TypeOfPublication).filter_by(name = name).count()
        if qty == 0:
            newPublicationType = TypeOfPublication(name=name)
            self.session.add(newPublicationType)
            self.session.commit()
            return newPublicationType
        else:
            return self.session.query(TypeOfPublication).filter_by(name = name).first()

    def indexPerson(self, personName):
        qty = self.session.query(Person).filter_by(name=personName).count()
        if qty == 0:
            newPerson = Person(name = personName)
            self.session.add(newPerson)
            self.session.commit()
            return newPerson
        else:
            return self.session.query(Person).filter_by(name=personName).first()

    def indexPersonPublication(self, personObj, publicationObj):
        qty = self.session.query(PersonPublication).filter_by(person=personObj, publication=publicationObj).count()
        if qty==0:
            newPersonPublication = PersonPublication(person=personObj, publication=publicationObj)
            self.session.add(newPersonPublication)
            self.session.commit()
            return newPersonPublication
        else:
            return self.session.query(PersonPublication).filter_by(person=personObj, publication=publicationObj).first()

    def indexJournal(self, journalName):
        qty = self.session.query(Journal).filter_by(name=journalName).count()
        if qty == 0:
            newJournal = Journal(name = journalName)
            self.session.add(newJournal)
            self.session.commit()
            return newJournal
        else:
            return self.session.query(Journal).filter_by(name=journalName).first()

    def indexPublications(self):
        for publicationType in self._types:
            start = time.clock()
            if verbose:
                total = int(self.conn.execute("XQUERY count(//%s)" % publicationType))
                print "Start to index publications of type %s (%d records)" % (publicationType, total)

            query = self.conn.query("for $publication in //%s return $publication" % publicationType)
            for typecode, item in query.iter():

                publicationTypeObj = self.indexPublicationType(publicationType)

                try:
                    publicationXML = xml.dom.minidom.parseString(unidecode(item)).documentElement
                except:
                    print "[ERROR] Publication with dblp_key %s is corrupted" % dblp_key

                journal = publicationXML.getElementsByTagName("journal")[0]
                journalObj = self.indexJournal(journal.firstChild.data)

                dblp_key = publicationXML.getAttribute("key")
                cont = 0
                qty = self.session.query(Publication).filter_by(dblp_key=dblp_key).count()
                if qty==0:
                    try:
                        title = publicationXML.getElementsByTagName("title")[0].firstChild.data

                        pages = pages = publicationXML.getElementsByTagName("pages")
                        if pages:
                            pages = pages[0].firstChild.data

                        year = int(publicationXML.getElementsByTagName("year")[0].firstChild.data)

                        volume = publicationXML.getElementsByTagName("volume")
                        if volume:
                            volume = volume[0].firstChild.data

                        number = publicationXML.getElementsByTagName("number")
                        if number:
                            number = number[0].firstChild.data

                        url = publicationXML.getElementsByTagName("url")
                        if url:
                            url = url[0].firstChild.data

                        ee = publicationXML.getElementsByTagName("ee")
                        if ee:
                            ee = ee[0].firstChild.data

                        newPublication = Publication(title=title, dblp_key=dblp_key, pages=pages, year=year, volume=volume,
                                                     number=number, ee=ee, url=url, journal=journalObj, type_of_publication=publicationTypeObj)
                        self.session.add(newPublication)
                        self.session.commit()

                        persons = publicationXML.getElementsByTagName("author")
                        for person in persons:
                            personObj = self.indexPerson(person.firstChild.data)
                            self.indexPersonPublication(personObj, newPublication)

                        cont+=1
                        if cont%100000 == 0:
                            print "%d publications are indexed" % cont
                    except:
                        print "[ERROR] Publication with dblp_key %s is corrupted" % dblp_key
            if verbose:
                print "End to index publications of type %s in %d ms" % (publicationType, int(time.clock() - start)*1000)





    def close(self):
        if self.conn:
            self.conn.close()


verbose = True

print "[START]"
start = time.clock()
i = Indexator("dblp", dbengine="postgresql+psycopg2://khrno:@localhost/dblp", verbose=verbose)
i.indexPublications()
i.close()
if verbose:
    print "\tDBLP dataset indexing complete in %d ms" % int(time.clock() - start) * 1000
print "[DONE]"
