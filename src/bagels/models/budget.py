from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from .database.db import Base


class Budget(Base):
    __tablename__ = "budget"

    createdAt = Column(DateTime, nullable=False, default=datetime.now)
    updatedAt = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
