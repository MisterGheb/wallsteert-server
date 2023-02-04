from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.orm import relationship

from .base import BaseModel
from ..constants import CONST_STRING_LENGTH, CONST_TOKEN_LENGTH
from .market_day import Market_day
from .stocks import Stocks

class Ohlcv(BaseModel):
    __tablename__ = 'ohlcv'
    
    open = Column(Numeric(12,2), nullable=False),
    high = Column(Numeric(12,2), nullable=False),
    low = Column(Numeric(12,2), nullable=False),
    close = Column(Numeric(12,2), nullable=False),
    volume = Column(Integer, nullable=False)
    id = Column(Integer, nullable=False)


    market_id = relationship('Market_day', back_populates='id')
    stock_id = relationship('Stocks', back_populates='id')