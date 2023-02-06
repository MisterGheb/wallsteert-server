from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from .base import BaseModel
from ..constants import CONST_STRING_LENGTH, CONST_TOKEN_LENGTH

class Market_day(BaseModel):
    __tablename__ = 'market_day'
    
    id = Column(Integer, primary_key=True)
    day = Column(Integer, nullable=False)
    status = Column(String(10), nullable=False)

    ohlcv = relationship('Ohlcv')




    

    