from models.category import Category
from models.database.db import db

def create_category(data):
    new_category = Category(**data)
    db.session.add(new_category)
    db.session.commit()
    return new_category

def get_all_categories():
    return Category.query.all()

def get_category_by_id(category_id):
    return Category.query.get(category_id)

def update_category(category_id, data):
    category = Category.query.get(category_id)
    if category:
        for key, value in data.items():
            setattr(category, key, value)
        db.session.commit()
    return category

def delete_category(category_id):
    category = Category.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        return True
    return False
