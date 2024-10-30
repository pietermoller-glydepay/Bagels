from models.database.app import get_app
from models.database.db import db
from models.person import Person

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
