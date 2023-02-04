from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from .base import BaseModel
from ..constants import CONST_STRING_LENGTH, CONST_TOKEN_LENGTH
from .note import Note

class User(BaseModel):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    username = Column(String(CONST_STRING_LENGTH), nullable=False)
    password = Column(String(CONST_STRING_LENGTH), nullable=False)
    first_name = Column(String(CONST_STRING_LENGTH), nullable=True)
    last_name = Column(String(CONST_STRING_LENGTH), nullable=True)
    token = Column(String(CONST_STRING_LENGTH), nullable=False)
    ad_username = Column(String(CONST_STRING_LENGTH), nullable=True)
    
    notes = relationship('Note', back_populates='created_by')
