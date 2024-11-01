from datetime import datetime, timedelta

from controllers.splits import (create_split, get_splits_by_record_id,
                                update_split)
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
        db.session.refresh(record)
        db.session.expunge(record)
        return record

def create_record_and_splits(record_data: dict, splits_data: list[dict]):
    with app.app_context():
        record = create_record(record_data)
        for split in splits_data:
            split['recordId'] = record.id
            create_split(split)
        return record

def get_record_by_id(record_id: int, populate_splits: bool = False):
    with app.app_context():
        query = Record.query.options(
            db.joinedload(Record.category),
            db.joinedload(Record.account)
        )
        
        if populate_splits:
            query = query.options(
                db.joinedload(Record.splits).options(
                    db.joinedload(Split.account),
                    db.joinedload(Split.person)
                )
            )
            
        record = query.get(record_id)
        return record

def get_records(start_time: datetime = None, end_time: datetime = None, month_offset: int = 0, sort_by: str = 'date', sort_direction: str = 'desc'):
    with app.app_context():
        query = Record.query.options(
            db.joinedload(Record.category),
            db.joinedload(Record.account),
            db.joinedload(Record.transferToAccount)
        )

        if start_time or end_time:
            if start_time:
                query = query.filter(Record.date >= start_time)
            if end_time:
                query = query.filter(Record.date <= end_time)
        else:    
            now = datetime.now()
            # Calculate target month and year
            target_month = now.month + month_offset
            target_year = now.year + (target_month - 1) // 12
            target_month = ((target_month - 1) % 12) + 1
            
            # Calculate next month and year for end date
            next_month = target_month + 1
            next_year = target_year + (next_month - 1) // 12
            next_month = ((next_month - 1) % 12) + 1
            
            start_of_month = datetime(target_year, target_month, 1)
            end_of_month = datetime(next_year, next_month, 1) - timedelta(microseconds=1)
            query = query.filter(Record.date >= start_of_month).filter(Record.date < end_of_month)

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
            db.session.refresh(record)
            db.session.expunge(record)
        return record

def update_record_and_splits(record_id: int, record_data: dict, splits_data: list[dict]):
    with app.app_context():
        record = update_record(record_id, record_data)
        record_splits = get_splits_by_record_id(record_id)
        for index, split in enumerate(record_splits):
            update_split(split.id, splits_data[index])
        return record

def delete_record(record_id: int):
    with app.app_context():
        record = Record.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return record
