from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database.db import Base


class Split(Base):
    __tablename__ = "split"

    createdAt = Column(DateTime, nullable=False, default=datetime.now)
    updatedAt = Column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    id = Column(Integer, primary_key=True, index=True)
    recordId = Column(
        Integer, ForeignKey("record.id", ondelete="CASCADE"), nullable=False
    )
    amount = Column(Float, nullable=False)
    personId = Column(Integer, ForeignKey("person.id"), nullable=False)
    isPaid = Column(Boolean, nullable=False, default=False)
    paidDate = Column(DateTime, nullable=True)
    accountId = Column(Integer, ForeignKey("account.id"), nullable=True)

    record = relationship("Record", foreign_keys=[recordId], back_populates="splits")
    person = relationship("Person", foreign_keys=[personId], back_populates="splits")
    account = relationship("Account", foreign_keys=[accountId], back_populates="splits")
