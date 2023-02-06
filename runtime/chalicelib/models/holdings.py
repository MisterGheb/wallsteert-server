from sqlalchemy import Column, String, Integer, Numeric, TIMESTAMP, Date, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel
from ..constants import CONST_STRING_LENGTH, CONST_TOKEN_LENGTH


class Holdings(BaseModel):
    __tablename__ = 'holdings'
    
    id = Column(Integer, primary_key=True)
    volume = Column(Numeric(12,2), nullable=False)
    bid_price = Column(String(4), nullable=False)
    bought_on = Column(Date, nullable=False)
    users_id = Column(Integer, ForeignKey("users.id"))
    stocks_id = Column(Integer, ForeignKey("stocks.id"))

    