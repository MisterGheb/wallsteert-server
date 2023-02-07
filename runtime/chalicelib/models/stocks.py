from sqlalchemy import Column, String, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

from .base import BaseModel
from ..constants import CONST_STRING_LENGTH, CONST_TOKEN_LENGTH
from .sectors import Sectors

class Stocks(BaseModel):
    __tablename__ = 'stocks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    total_volume = Column(Integer, nullable=False)
    unallocated = Column(Integer, nullable=False)
    price = Column(Numeric(12,2), nullable=False)
    sectors_id = Column(Integer, ForeignKey("sectors.id"))

