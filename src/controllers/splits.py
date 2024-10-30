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

def delete_splits_by_record_id(record_id):
    with app.app_context():
        Split.query.filter_by(recordId=record_id).delete()
        db.session.commit()