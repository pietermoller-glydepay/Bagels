from models.record import Record
from models.database.db import db
from models.database.app import get_app

app = get_app()

def create_record(record_data: dict):
    with app.app_context():
        record = Record(**record_data)
        db.session.add(record)
        db.session.commit()
        return (record.date, record.description, record.amount)

def getRecordTableRows():
    with app.app_context():
        records = Record.query.join(Record.category).all()
        arr = []
        for record in records:
            match record.isAllUnpaidCleared:
                case True:
                    T = "✔︎"
                case False:
                    T = "⊙"
                case _:
                    T = ""
                
            arr.append((T, record.date, record.category.name, record.amount, record.label))
        return arr

def get_record(record_id: int):
    with app.app_context():
        return Record.query.get(record_id)

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
