from sqlalchemy import Column, String, Integer, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from .base import BaseModel
from .stocks import Stocks
from ..constants import CONST_STRING_LENGTH, CONST_TOKEN_LENGTH



class Ohlcv(BaseModel):
    __tablename__ = 'ohlcv'
    
    open = Column(Numeric(12,2), nullable=False)
    high = Column(Numeric(12,2), nullable=False)
    low = Column(Numeric(12,2), nullable=False)
    close = Column(Numeric(12,2), nullable=False)
    volume = Column(Integer, nullable=False)
    id = Column(Integer, primary_key=True)
    market_id = Column(Integer, ForeignKey("market_day.id"))
    stocks_id = Column(Integer, ForeignKey("stocks.id"))

   