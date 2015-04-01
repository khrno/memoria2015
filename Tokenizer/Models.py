import datetime

from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Publication(Base):
    __tablename__ = "publication"
    id = Column(Integer, primary_key=True)
    title = Column(Text, nullable=False)
    dblp_key = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(Integer, nullable=False, default=1)


class Token(Base):
    __tablename__ = "token"
    id = Column(Integer, primary_key=True)
    token = Column(Text, nullable=False, unique=True)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(Integer, nullable=False, default=1)


class Ocurrence(Base):
    __tablename__ = "ocurrence"
    id = Column(Integer, primary_key=True)
    publication_id = Column(Integer, ForeignKey('publication.id'), nullable=False)
    publication = relationship(Publication)
    token_id = Column(Integer, ForeignKey('token.id'), nullable=False)
    token = relationship(Token)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(Integer, nullable=False, default=1)


class Bigram(Base):
    __tablename__ = "bigram"
    id = Column(Integer, primary_key=True)
    bigram = Column(Text, nullable=False, unique=True)
    score_type = Column(Text, nullable=False, default="raw_freq")
    score = Column(Float, nullable=False, default=0.0)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(Integer, nullable=False, default=1)


class OcurrenceBigram(Base):
    __tablename__ = "ocurrence_bigram"
    id = Column(Integer, primary_key=True)
    publication_id = Column(Integer, ForeignKey('publication.id'), nullable=False)
    publication = relationship(Publication)
    bigram_id = Column(Integer, ForeignKey('bigram.id'), nullable=False)
    bigram = relationship(Bigram)
    creation_datetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    status = Column(Integer, nullable=False, default=1)


if __name__ == "__main__":
    engine = create_engine('postgresql+psycopg2://khrno:@localhost/dblp_v2')
    Base.metadata.create_all(engine)