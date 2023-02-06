from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from .base import BaseModel
from ..constants import CONST_STRING_LENGTH, CONST_TOKEN_LENGTH

class Users(BaseModel):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(50),nullable=False)
    available_funds = Column(Numeric(12,2), nullable=False)
    blocked_funds = Column(Numeric(12,2), nullable=False)

    orders = relationship('Orders')
    holdings = relationship('Holdings')