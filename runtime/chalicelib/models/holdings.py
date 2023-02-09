from sqlalchemy import Column, String, Integer, Numeric, TIMESTAMP, Date, ForeignKey
from sqlalchemy.orm import relationship


from .base import BaseModel
from .users import Users
from ..constants import CONST_STRING_LENGTH, CONST_TOKEN_LENGTH


class Holdings(BaseModel):
    __tablename__ = 'holdings'
    
    id = Column(Integer, primary_key=True)
    volume = Column(Integer(), nullable=False)
    bid_price = Column(Numeric(12,2), nullable=False)
    bought_on = Column(Date, nullable=False)
    users_id = Column(Integer, ForeignKey("users.id"))
    stocks_id = Column(Integer, ForeignKey("stocks.id"))

    users = relationship('Users')
    stocks = relationship("Stocks")