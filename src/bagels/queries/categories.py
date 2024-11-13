from datetime import datetime
from rich.text import Text

from bagels.models.category import Category
from bagels.models.database.app import get_app
from bagels.models.database.db import db
from bagels.models.record import Record
from bagels.queries.utils import get_start_end_of_period

app = get_app()


def _get_base_categories_query(include_deleted=False):
    query = Category.query
    if not include_deleted:
        query = query.filter(Category.deletedAt.is_(None))
    return query


# region Get
def get_categories_count():
    with app.app_context():
        return _get_base_categories_query().count()


def get_all_categories_tree():  # special function to get the categories in a tree format
    with app.app_context():
        # Fetch all categories
        categories = (
            _get_base_categories_query()
            .options(db.joinedload(Category.parentCategory))
            .order_by(Category.id)
            .all()
        )

        # Helper function to recursively build the category tree
        def build_category_tree(parent_id=None, depth=0):
            result = []
            for category in categories:
                if category.parentCategoryId == parent_id:
                    # Determine the node symbol based on depth
                    if depth == 0:
                        node = Text("●", style=category.color)
                    else:
                        node = Text(
                            " " * (depth - 1)
                            + ("└" if is_last(category, parent_id) else "├"),
                            style=category.color,
                        )

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
        categories = (
            db.session.query(
                Category, db.func.count(Category.records).label("record_count")
            )
            .outerjoin(Category.records)
            .group_by(Category.id)
            .order_by(db.desc("record_count"))
            .options(db.joinedload(Category.parentCategory))
            .filter(Category.deletedAt.is_(None))
            .all()
        )

        return categories


def get_category_by_id(category_id):
    with app.app_context():
        return _get_base_categories_query().get(category_id)


def get_all_categories_records(
    offset: int = 0,
    offset_type: str = "month",
    is_income: bool = True,
    subcategories: bool = False,
    account_id: int = None,
):
    """
    Returns all categories, sorted by the total net amount of expense/income of records in that category.

    Rules:
    - Filter applies to only to records (date, account). Splits must always be considered by their associated records.
    - Income and expenses should be calculated from record less their splits, regardless of the account of the split.
    - Populate categories.amount with the net total amount of expense/income in that category.
    - If subcategories is False, group all amounts (income/expense) to their parent category
    - Only return categories with non-zero amounts.
    - Sort categories by the total net amount of expense/income.

    Args:
        accountId (int): The ID of the account to filter by. (Optional)
        offset_type (str): The type of period to filter by.
        offset (int): The offset from the current period.
        is_income (bool): Whether to filter by income or expense.
        subcategories (bool): Whether to include subcategories in the result
    """
    with app.app_context():
        # Get start and end dates for the period
        start_of_period, end_of_period = get_start_end_of_period(offset, offset_type)

        # Query records within the specified period and account
        query = db.session.query(Record).options(db.joinedload(Record.category))
        if account_id is not None:
            query = query.filter(Record.accountId == account_id)
        query = query.filter(
            Record.date >= start_of_period,
            Record.date < end_of_period,
            Record.isIncome == is_income,
        )

        # Calculate net amounts for each category
        category_totals = {}
        records = query.all()
        for record in records:

            split_total = sum(split.amount for split in record.splits)
            record_amount = record.amount - split_total

            if record.category is None:
                continue

            category_id = record.categoryId
            if not subcategories and record.category.parentCategoryId:
                category_id = record.category.parentCategoryId

            if category_id not in category_totals:
                category_totals[category_id] = 0
            category_totals[category_id] += record_amount

        # Filter out categories with zero amounts and sort by net amount
        categories = (
            db.session.query(Category)
            .filter(
                Category.id.in_(category_totals.keys()), Category.deletedAt.is_(None)
            )
            .all()
        )
        for category in categories:
            category.amount = category_totals[category.id]

        categories = [cat for cat in categories if cat.amount != 0]
        categories.sort(key=lambda cat: cat.amount, reverse=True)

        return categories


# region Create
def create_category(data):
    with app.app_context():
        new_category = Category(**data)
        db.session.add(new_category)
        db.session.commit()
        db.session.refresh(new_category)
        db.session.expunge(new_category)
        return new_category


# region Update
def update_category(category_id, data):
    with app.app_context():
        category = Category.query.get(category_id)
        if category:
            for key, value in data.items():
                setattr(category, key, value)
            db.session.commit()
        return category


# region Delete
def delete_category(category_id):
    with app.app_context():
        category = Category.query.get(category_id)
        if category:
            category.deletedAt = datetime.now()
            db.session.commit()
            db.session.refresh(category)
            db.session.expunge(category)
            return True
        return False
