from models.person import Person
from models.database.db import db

def create_person(data):
    new_person = Person(**data)
    db.session.add(new_person)
    db.session.commit()
    return new_person

def get_all_persons():
    return Person.query.all()

def get_person_by_id(person_id):
    return Person.query.get(person_id)

def update_person(person_id, data):
    person = Person.query.get(person_id)
    if person:
        for key, value in data.items():
            setattr(person, key, value)
        db.session.commit()
    return person

def delete_person(person_id):
    person = Person.query.get(person_id)
    if person:
        db.session.delete(person)
        db.session.commit()
        return True
    return False
