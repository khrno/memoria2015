import datetime

from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class TypeOfPublication(Base):
    __tablename__ = "type_of_publication"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    qty_publications = Column(Integer, nullable=False, default=0)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(Integer, nullable=False, default=1)

class Journal(Base):
    __tablename__ = "journal"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    code = Column(Text, nullable=True, default=None)
    qty_publications = Column(Integer, nullable=False, default=0)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(Integer, nullable=False, default=1)


class Publication(Base):
    __tablename__ = "publication"
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    dblp_key = Column(Text, nullable=False)
    pages = Column(Text, nullable=True, default=None)
    year = Column(Integer, nullable=False)
    volume = Column(Text, nullable=True, default=None)
    number = Column(Text, nullable=True, default=None)
    ee = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    type_of_publication_id = Column(Integer, ForeignKey('type_of_publication.id'), nullable=False)
    type_of_publication = relationship(TypeOfPublication)
    journal_id = Column(Integer, ForeignKey('journal.id'),nullable=False)
    journal = relationship(Journal)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(Integer, nullable=False, default=1)

class Person(Base):
    __tablename__ = "person"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    url = Column(Text, nullable=True, default=None)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(Integer, nullable=False, default=1)

class PersonPublication(Base):
    __tablename__ = "person_publication"
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('person.id'), nullable=False)
    person = relationship(Person)
    publication_id = Column(Integer, ForeignKey('publication.id'), nullable=False)
    publication = relationship(Publication)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(Integer, nullable=False, default=1)


engine = create_engine('postgresql+psycopg2://khrno:@localhost/dblp')
Base.metadata.create_all(engine)