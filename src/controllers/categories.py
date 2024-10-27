from rich.text import Text

from models.category import Category, Nature
from models.database.app import get_app
from models.database.db import db

app = get_app()

def create_default_categories():
    with app.app_context():
        sample_categories = [
            {"name": "Test", "parentCategoryId": 6, "nature": Nature.MUST, "color": "#900C3F"},
        ]
        for category_data in sample_categories:
            category = Category(**category_data)
            db.session.add(category)
        db.session.commit()

def create_category(data):
    with app.app_context():
        new_category = Category(**data)
        db.session.add(new_category)
        db.session.commit()
        return new_category

def get_all_categories(): # special function to get the categories in a tree format
    with app.app_context():
        # Fetch all categories
        categories = Category.query.order_by(Category.id).all()

        # Helper function to recursively build the category tree
        def build_category_tree(parent_id=None, depth=0):
            result = []
            for category in categories:
                if category.parentCategoryId == parent_id:
                    # Determine the node symbol based on depth
                    if depth == 0:
                        node = Text("●", style=category.color)
                    else:
                        node = " " * (depth - 1) + ("└" if is_last(category, parent_id) else "├")
                    
                    result.append((category, node))
                    # Recursively add subcategories with increased depth
                    result.extend(build_category_tree(category.id, depth + 1))
            return result

        def is_last(category, parent_id):
            siblings = [cat for cat in categories if cat.parentCategoryId == parent_id]
            return category == siblings[-1]

        return build_category_tree()

def get_category_by_id(category_id):
    with app.app_context():
        return Category.query.get(category_id)  

def update_category(category_id, data):
    with app.app_context():
        category = Category.query.get(category_id)
        if category:
            for key, value in data.items():
                setattr(category, key, value)
            db.session.commit()
        return category

def delete_category(category_id):
    with app.app_context():
        category = Category.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
            return True
        return False