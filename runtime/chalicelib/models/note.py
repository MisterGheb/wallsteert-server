from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel
from ..constants import CONST_PARAGRAPH_LENGTH

class Note(BaseModel):
    __tablename__ = 'note'

    id = Column(Integer, primary_key=True)
    content = Column(String(CONST_PARAGRAPH_LENGTH), nullable=True)
    created_by_id = Column(Integer, ForeignKey('user.id'))

    created_by = relationship('User', back_populates='notes')
