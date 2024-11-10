from pathlib import Path

import yaml
from rich.text import Text

from bagels.models.category import Category, Nature
from bagels.models.database.app import get_app
from bagels.models.database.db import db
from bagels.models.record import Record
from bagels.queries.utils import get_start_end_of_period

app = get_app()
        
#region Get
def get_categories_count():
    with app.app_context():
        return Category.query.count()

def get_all_categories_tree(): # special function to get the categories in a tree format
    with app.app_context():
        # Fetch all categories
        categories = Category.query.options(db.joinedload(Category.parentCategory)).order_by(Category.id).all()

        # Helper function to recursively build the category tree
        def build_category_tree(parent_id=None, depth=0):
            result = []
            for category in categories:
                if category.parentCategoryId == parent_id:
                    # Determine the node symbol based on depth
                    if depth == 0:
                        node = Text("●", style=category.color)
                    else:
                        node = Text(" " * (depth - 1) + ("└" if is_last(category, parent_id) else "├"), style=category.color)
                    
                    result.append((category, node))
                    # Recursively add subcategories with increased depth
                    result.extend(build_category_tree(category.id, depth + 1))
            return result

        def is_last(category, parent_id):
            siblings = [cat for cat in categories if cat.parentCategoryId == parent_id]
            return category == siblings[-1]

        return build_category_tree()

def get_all_categories_by_freq():
    with app.app_context():
        # Query categories and count their usage in records
        categories = db.session.query(
            Category,
            db.func.count(Category.records).label('record_count')
        ).outerjoin(Category.records)\
         .group_by(Category.id)\
         .order_by(db.desc('record_count'))\
         .options(db.joinedload(Category.parentCategory))\
         .all()
        
        return categories

def get_category_by_id(category_id):
    with app.app_context():
        return Category.query.get(category_id)  

def get_all_categories_records(offset: int = 0, offset_type: str = "month", record_limit: int = 3, isExpense: bool = True, subcategories: bool = False, account_id: int = None):
    # Get all the categories sorted by the total net amount of expense/income of records in that category
    # Populate categories.records with the last record_limit records
    # Categories should have the net amount and the percentage of net/total amount
    with app.app_context():
        # Get start and end dates for the period
        start_of_period, end_of_period = get_start_end_of_period(offset, offset_type)

        # Base query with account filter if provided
        base_query = db.session.query(
            Category,
            db.func.sum(Record.amount).label('net_amount')
        ).join(Category.records)\
         .filter(Record.date >= start_of_period)\
         .filter(Record.date < end_of_period)\
         .filter(Record.isIncome == (not isExpense))
        
        if account_id is not None:
            base_query = base_query.filter(Record.accountId == account_id)

        if subcategories:
            categories = base_query\
                .group_by(Category.id)\
                .order_by(db.desc('net_amount'))\
                .all()
        else:
            categories = base_query\
                .group_by(Category.id)\
                .order_by(db.desc('net_amount'))\
                .all()

            # Aggregate subcategories into their parent categories
            category_dict = {}
            for category, net_amount in categories:
                parent_id = category.parentCategoryId if category.parentCategoryId else category.id
                parent_category = category.parentCategory if category.parentCategory else category
                if parent_id not in category_dict:
                    category_dict[parent_id] = [parent_category, 0]
                category_dict[parent_id][1] += net_amount or 0

            categories = list(category_dict.values())

        # Calculate total amount across all categories
        total_amount = sum(abs(cat[1] or 0) for cat in categories)

        # Format results and fetch recent records
        result = []
        for category, net_amount in categories:
            # Get recent records for this category with account filter if provided
            recent_records_query = Record.query\
                .filter(Record.categoryId == category.id)\
                .filter(Record.date >= start_of_period)\
                .filter(Record.date < end_of_period)\
                .filter(Record.isIncome == (not isExpense))
            
            if account_id is not None:
                recent_records_query = recent_records_query.filter(Record.accountId == account_id)
                
            recent_records = recent_records_query\
                .order_by(Record.date.desc())\
                .limit(record_limit)\
                .all()

            # Add computed fields
            category.records = recent_records
            category.net_amount = abs(net_amount or 0)
            category.percentage = int((abs(net_amount or 0) / total_amount * 100)) if total_amount > 0 else 0

            result.append(category)

        # Sort the result by percentage
        result.sort(key=lambda cat: cat.percentage, reverse=True)

        return result

#region Create
def create_category(data):
    with app.app_context():
        new_category = Category(**data)
        db.session.add(new_category)
        db.session.commit()
        db.session.refresh(new_category)
        db.session.expunge(new_category)
        return new_category

#region Update
def update_category(category_id, data):
    with app.app_context():
        category = Category.query.get(category_id)
        if category:
            for key, value in data.items():
                setattr(category, key, value)
            db.session.commit()
        return category

#region Delete
def delete_category(category_id):
    with app.app_context():
        category = Category.query.get(category_id)
        if category:
            db.session.delete(category)
            db.session.commit()
            return True
        return False

#region Default
def create_default_categories():
    # Get the path to the YAML file
    yaml_path = Path(__file__).parent.parent / "templates" / "default_categories.yaml"
    
    with open(yaml_path, 'r') as file:
        default_categories = yaml.safe_load(file)

    with app.app_context():
        for category in default_categories:
            parent = create_category({
                "name": category["name"],
                "nature": getattr(Nature, category["nature"]),
                "color": category["color"], 
                "parentCategoryId": None
            })

            for subcategory in category["subcategories"]:
                create_category({
                    "name": subcategory["name"],
                    "nature": getattr(Nature, subcategory["nature"]),
                    "color": category["color"],
                    "parentCategoryId": parent.id
                })