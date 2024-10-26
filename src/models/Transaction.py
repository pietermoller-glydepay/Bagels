from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Model(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime)
    description = Column(String)
    amount = Column(Float)
    # category = Column(String)

FORM = [
    {
        "placeholder": "dd (mm) (yy)",
        "title": "Date",
        "type": "dateAutoDay",
        "defaultValue": datetime.now().strftime("%d")
    },
    {
        "placeholder": "Description",
        "title": "Description",
        "type": "string",
    },
    {
        "placeholder": "Amount",
        "title": "Amount",
        "type": "number",
    },
    # "category": "text",
]
