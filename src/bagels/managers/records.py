from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import joinedload, sessionmaker

from bagels.managers.splits import create_split, get_splits_by_record_id, update_split
from bagels.managers.utils import get_operator_amount, get_start_end_of_period
from bagels.models.category import Category
from bagels.models.database.app import db_engine
from bagels.models.record import Record
from bagels.models.split import Split

Session = sessionmaker(bind=db_engine)


# region Create
def create_record(record_data: dict):
    session = Session()
    try:
        record = Record(**record_data)
        session.add(record)
        session.commit()
        session.refresh(record)
        session.expunge(record)
        return record
    finally:
        session.close()


def create_record_and_splits(record_data: dict, splits_data: list[dict]):
    session = Session()
    try:
        record = create_record(record_data)
        for split in splits_data:
            split["recordId"] = record.id
            create_split(split)
        return record
    finally:
        session.close()


# region Get
def get_record_by_id(record_id: int, populate_splits: bool = False):
    session = Session()
    try:
        query = session.query(Record).options(
            joinedload(Record.category), joinedload(Record.account)
        )

        if populate_splits:
            query = query.options(
                joinedload(Record.splits).options(
                    joinedload(Split.account), joinedload(Split.person)
                )
            )

        record = query.get(record_id)
        return record
    finally:
        session.close()


def get_record_total_split_amount(record_id: int):
    session = Session()
    try:
        splits = get_splits_by_record_id(record_id)
        return sum(split.amount for split in splits)
    finally:
        session.close()


def get_records(
    offset: int = 0,
    offset_type: str = "month",
    account_id: int = None,
    category_piped_names: str = None,
    operator_amount: str = None,
    label: str = None,
):
    session = Session()
    try:
        query = session.query(Record).options(
            joinedload(Record.category),
            joinedload(Record.account),
            joinedload(Record.transferToAccount),
            joinedload(Record.splits).options(
                joinedload(Split.account), joinedload(Split.person)
            ),
        )

        start_of_period, end_of_period = get_start_end_of_period(offset, offset_type)
        query = query.filter(
            Record.date >= start_of_period, Record.date < end_of_period
        )

        if account_id not in [None, ""]:
            query = query.filter(Record.accountId == account_id)
        if category_piped_names not in [None, ""]:
            category_names = category_piped_names.split("|")
            query = query.join(Record.category).filter(
                Category.name.in_(category_names)
            )
        if operator_amount not in [None, ""]:
            operator, amount = get_operator_amount(operator_amount)
            if operator and amount:
                query = query.filter(Record.amount.op(operator)(amount))
        if label not in [None, ""]:
            query = query.filter(Record.label.ilike(f"%{label}%"))

        createdAt_column = getattr(Record, "createdAt")
        date_column = func.date(getattr(Record, "date"))
        query = query.order_by(date_column.desc(), createdAt_column.desc())

        records = query.all()
        return records
    finally:
        session.close()


def get_spending_trend(weeks=1, week_offset=0) -> list[float]:
    """Gets a list of spent amounts for the last x weeks, less split amounts of the records. Considers only isIncome=False"""
    session = Session()
    try:
        # Get records for the specified weeks
        start_date = datetime.now() - timedelta(weeks=weeks)
        end_date = datetime.now() - timedelta(weeks=week_offset)
        records = (
            session.query(Record)
            .filter(
                Record.isIncome == False,  # noqa: E712
                Record.date >= start_date,
                Record.date <= end_date,
                Record.isTransfer == False,  # noqa: E712
            )
            .options(joinedload(Record.splits))
            .all()
        )

        # Calculate spending per day
        daily_spending = {}
        for record in records:
            date_key = record.date.date()
            splits_sum = sum(split.amount for split in record.splits)
            actual_spend = record.amount - splits_sum

            if date_key in daily_spending:
                daily_spending[date_key] += actual_spend
            else:
                daily_spending[date_key] = actual_spend

        # Create list of daily spending
        sorted_dates = sorted(daily_spending.keys())
        spending_trend = [daily_spending[date] for date in sorted_dates]

        return spending_trend
    finally:
        session.close()


def is_record_all_splits_paid(record_id: int):
    session = Session()
    try:
        splits = get_splits_by_record_id(record_id)
        return all(split.isPaid for split in splits)
    finally:
        session.close()


# region Update
def update_record(record_id: int, updated_data: dict):
    session = Session()
    try:
        record = session.query(Record).get(record_id)
        if record:
            for key, value in updated_data.items():
                setattr(record, key, value)
            session.commit()
            session.refresh(record)
            session.expunge(record)
        return record
    finally:
        session.close()


def update_record_and_splits(
    record_id: int, record_data: dict, splits_data: list[dict]
):
    session = Session()
    try:
        record = update_record(record_id, record_data)
        record_splits = get_splits_by_record_id(record_id)
        for index, split in enumerate(record_splits):
            update_split(split.id, splits_data[index])
        return record
    finally:
        session.close()


# region Delete
def delete_record(record_id: int):
    session = Session()
    try:
        record = session.query(Record).get(record_id)
        if record:
            session.delete(record)
            session.commit()
        return record
    finally:
        session.close()
