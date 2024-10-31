from datetime import datetime, timedelta

from models.account import Account
from models.category import Category
from models.database.app import get_app
from models.database.db import db
from models.record import Record
from models.split import Split

app = get_app()

def create_record(record_data: dict):
    with app.app_context():
        record = Record(**record_data)
        db.session.add(record)
        db.session.commit()
        return record

def get_record_by_id(record_id: int, populate_splits: bool = False):
    with app.app_context():
        record = Record.query.options(
            db.joinedload(Record.category),
            db.joinedload(Record.account),
            db.joinedload(Record.splits).joinedload(Split.account) if populate_splits else None
        ).get(record_id)
        return record

def get_records(start_time: datetime = None, end_time: datetime = None, sort_by: str = 'date', sort_direction: str = 'desc'):
    with app.app_context():
        query = Record.query.options(
            db.joinedload(Record.category),
            db.joinedload(Record.account),
            db.joinedload(Record.transferToAccount)
        )

        if start_time:
            query = query.filter(Record.date >= start_time)
        if end_time:
            query = query.filter(Record.date <= end_time)

        if sort_by:
            column = getattr(Record, sort_by)
            if sort_direction.lower() == 'asc':
                query = query.order_by(column.asc())
            else:
                query = query.order_by(column.desc())

        records = query.all()
        return records

def update_record(record_id: int, updated_data: dict):
    with app.app_context():
        record = Record.query.get(record_id)
        if record:
            for key, value in updated_data.items():
                setattr(record, key, value)
            db.session.commit()
        return record

def delete_record(record_id: int):
    with app.app_context():
        record = Record.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return record
