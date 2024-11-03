from datetime import datetime
from enum import Enum

from .database.db import db


class Nature(Enum):
    WANT = "Want"
    NEED = "Need"
    MUST = "Must"

    def __str__(self):
        return self.value

class Category(db.Model):
    __tablename__ = "category"
    
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    id = db.Column(db.Integer, primary_key=True, index=True)
    parentCategoryId = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    name = db.Column(db.String, nullable=False)
    nature = db.Column(db.Enum(Nature), nullable=False)
    color = db.Column(db.String, nullable=False)
    
    records = db.relationship("Record", back_populates="category")
    parentCategory = db.relationship("Category", back_populates="subCategories", remote_side=[id])
    subCategories = db.relationship("Category", back_populates="parentCategory", remote_side=[parentCategoryId])
