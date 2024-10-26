from enum import Enum

from .database.db import db


class Nature(Enum):
    WANT = "want"
    NEED = "need"
    MUST = "must"

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True, index=True)
    parentCategoryId = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    name = db.Column(db.String, nullable=False)
    nature = db.Column(db.Enum(Nature), nullable=False)
    color = db.Column(db.String)