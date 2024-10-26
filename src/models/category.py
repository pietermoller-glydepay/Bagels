from .database.db import db

class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True, index=True)
    parentCategoryId = db.Column(db.Integer, db.ForeignKey("category.id"))
    name = db.Column(db.String)
    nature = db.Column(db.String)
    color = db.Column(db.String)

COLUMNS = []