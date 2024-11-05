from models.database.app import get_app
from models.database.db import db
from models.split import Split

app = get_app()

def create_split(data):
    with app.app_context():
        new_split = Split(**data)
        db.session.add(new_split)
        db.session.commit()
        return new_split

def get_splits_by_record_id(record_id):
    with app.app_context():
        return Split.query.filter_by(recordId=record_id).all()

def get_split_by_id(split_id):
    with app.app_context():
        return Split.query.get(split_id)

def update_split(split_id, updated_data):
    with app.app_context():
        split = Split.query.get(split_id)
        if split:
            for key, value in updated_data.items():
                setattr(split, key, value)
            db.session.commit()
        return split

def delete_split(split_id):
    with app.app_context():
        split = Split.query.get(split_id)
        if split:
            db.session.delete(split)
            db.session.commit()
        return split

def delete_splits_by_record_id(record_id):
    with app.app_context():
        Split.query.filter_by(recordId=record_id).delete()
        db.session.commit()
