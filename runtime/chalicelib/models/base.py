from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy_mixins import AllFeaturesMixin, TimestampsMixin

from ..constants import DB_ENDPOINT

Base = declarative_base()


class BaseModel(Base, AllFeaturesMixin, TimestampsMixin):
    __abstract__ = True


engine = create_engine(DB_ENDPOINT, echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit=True))

BaseModel.set_session(session)
