"""Helper class to get a database engine and a session."""
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils.functions import database_exists, create_database

from pornhub.config import config

engine = create_engine(config['sql_uri'])
base = declarative_base(bind=engine)


def get_session():
    """Get a new scoped session."""
    session = scoped_session(sessionmaker(bind=engine))
    return session


def create_db():
    """Create db if it doesn't exist yet."""
    db_url = engine.url
    if not database_exists(db_url):
        create_database(db_url)
        base.metadata.create_all()
