from datetime import datetime

from sqlalchemy import and_

from models.database.app import get_app
from models.database.db import db
from models.person import Person
from models.record import Record
from models.split import Split

app = get_app()

def create_person(data):
    with app.app_context():
        new_person = Person(**data)
        db.session.add(new_person)
        db.session.commit()
        return new_person

def get_all_persons():
    with app.app_context():
        return Person.query.all()

def get_person_by_id(person_id):
    with app.app_context():
        return Person.query.get(person_id)

def update_person(person_id, data):
    with app.app_context():
        person = Person.query.get(person_id)
        if person:
            for key, value in data.items():
                setattr(person, key, value)
            db.session.commit()
        return person

def delete_person(person_id):
    with app.app_context():
        person = Person.query.get(person_id)
        if person:
            db.session.delete(person)
            db.session.commit()
            return True
        return False

def get_persons_with_splits(month_offset=0):
    """Get all persons with their splits for the specified month"""
    with app.app_context():
        today = datetime.now()
        year = today.year
        month = today.month + month_offset
        
        # Adjust year if month goes out of bounds
        while month < 1:
            month += 12
            year -= 1
        while month > 12:
            month -= 12
            year += 1
            
        # Get start and end dates for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        return Person.query.options(
            db.joinedload(Person.splits)
            .joinedload(Split.record)
            .joinedload(Record.category),
            db.joinedload(Person.splits)
            .joinedload(Split.account),
        ).join(Person.splits).join(Split.record).filter(
            and_(
                Record.date >= start_date,
                Record.date < end_date
            )
        ).order_by(Record.date.asc()).distinct().all()
