from models.unpaidRecord import UnpaidRecord
from models.database.db import db

def create_unpaid_record(data):
    new_unpaid_record = UnpaidRecord(**data)
    db.session.add(new_unpaid_record)
    db.session.commit()
    return new_unpaid_record

def get_all_unpaid_records():
    return UnpaidRecord.query.all()

def get_unpaid_record_by_id(unpaid_record_id):
    return UnpaidRecord.query.get(unpaid_record_id)

def update_unpaid_record(unpaid_record_id, data):
    unpaid_record = UnpaidRecord.query.get(unpaid_record_id)
    if unpaid_record:
        for key, value in data.items():
            setattr(unpaid_record, key, value)
        db.session.commit()
    return unpaid_record

def delete_unpaid_record(unpaid_record_id):
    unpaid_record = UnpaidRecord.query.get(unpaid_record_id)
    if unpaid_record:
        db.session.delete(unpaid_record)
        db.session.commit()
        return True
    return False
