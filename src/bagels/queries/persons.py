from datetime import datetime

from sqlalchemy import and_

from bagels.models.database.app import get_app
from bagels.models.database.db import db
from bagels.models.person import Person
from bagels.models.record import Record
from bagels.models.split import Split
from bagels.queries.utils import get_start_end_of_period

app = get_app()

def create_person(data):
    with app.app_context():
        new_person = Person(**data)
        db.session.add(new_person)
        db.session.commit()
        db.session.refresh(new_person)
        db.session.expunge(new_person)
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

def get_persons_with_splits(offset: int = 0, offset_type: str = "month"):
    """Get all persons with their splits for the specified period"""
    with app.app_context():
        start_of_period, end_of_period = get_start_end_of_period(offset, offset_type)       
        return Person.query.options(
            db.joinedload(Person.splits)
            .joinedload(Split.record)
            .joinedload(Record.category),
            db.joinedload(Person.splits)
            .joinedload(Split.account),
        ).join(Person.splits).join(Split.record).filter(
            and_(
                Record.date >= start_of_period,
                Record.date < end_of_period
            )
        ).order_by(Record.date.asc()).distinct().all()
