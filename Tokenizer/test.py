from Models import Publication, Token, Ocurrence
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import codecs

Base = declarative_base()
engine = create_engine('postgresql+psycopg2://khrno:@localhost/dblp_v2')
DBSession = sessionmaker()
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db = DBSession()


engine = create_engine("postgresql+psycopg2://khrno:@localhost/dblp_v2")
# SELECT t.token FROM token as t, ocurrence as o, publication as p WHERE p.type='mastersthesis' and o.publication_id = p.id and o.token_id = t.id;
# publications = db.query(Publication).filter_by(type='mastersthesis').all()


print db.query(Token).join(Ocurrence.token)