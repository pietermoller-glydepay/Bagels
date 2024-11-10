from datetime import datetime

from .database.db import db


class Person(db.Model):
    __tablename__ = "person"
    
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String)
    
    splits = db.relationship("Split", back_populates="person")