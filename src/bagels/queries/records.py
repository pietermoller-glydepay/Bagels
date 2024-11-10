from bagels.models.database.app import get_app
from bagels.models.database.db import db
from bagels.models.record import Record
from bagels.models.split import Split
from bagels.queries.splits import (create_split, get_splits_by_record_id,
                                   update_split)
from bagels.queries.utils import get_start_end_of_period

app = get_app()
#region Create
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


#region Get
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

def get_record_total_split_amount(record_id: int):
    with app.app_context():
        splits = get_splits_by_record_id(record_id)
        return sum(split.amount for split in splits)

def get_records(offset: int = 0, offset_type: str = "month"):
    with app.app_context():
        query = Record.query.options(
            db.joinedload(Record.category),
            db.joinedload(Record.account),
            db.joinedload(Record.transferToAccount),
            db.joinedload(Record.splits).options(
                db.joinedload(Split.account),
                db.joinedload(Split.person)
            )
        )

        start_of_period, end_of_period = get_start_end_of_period(offset, offset_type)
        query = query.filter(Record.date >= start_of_period, 
                             Record.date < end_of_period)

        createdAt_column = getattr(Record, "createdAt")
        date_column = getattr(Record, "date")
        query = query.order_by(date_column.desc(), createdAt_column.desc())

        records = query.all()
        return records

def is_record_all_splits_paid(record_id: int):
    with app.app_context():
        splits = get_splits_by_record_id(record_id)
        return all(split.isPaid for split in splits)

#region Update
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

#region Delete
def delete_record(record_id: int):
    with app.app_context():
        record = Record.query.get(record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
        return record
