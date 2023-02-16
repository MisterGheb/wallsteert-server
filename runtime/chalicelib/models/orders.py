
from sqlalchemy import Column, String, Integer, Numeric, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey,DateTime
from sqlalchemy.sql import func

from .base import BaseModel
from ..constants import CONST_STRING_LENGTH, CONST_TOKEN_LENGTH
from .users import Users
from .stocks import Stocks

class Orders(BaseModel):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    bid_price = Column(Numeric(12,2), nullable=False)
    type = Column(String(4), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(String(20), nullable=False)
    bid_volume = Column(Integer, nullable=False)
    executed_volume = Column(Integer, nullable=False)
    stocks_id = Column(Integer, ForeignKey("stocks.id"))
    users_id = Column(Integer, ForeignKey("users.id"))


