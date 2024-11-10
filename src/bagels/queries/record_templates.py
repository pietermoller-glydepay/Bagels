from bagels.models.database.app import get_app
from bagels.models.database.db import db
from bagels.models.record_template import RecordTemplate

app = get_app()

#region c
def create_template(data):
    with app.app_context():
        new_template = RecordTemplate(**data)
        db.session.add(new_template)
        db.session.commit()
        return new_template

#region r
def get_all_templates():
    with app.app_context():
        return RecordTemplate.query.options(
            db.joinedload(RecordTemplate.category),
            db.joinedload(RecordTemplate.account)
        ).all()

def get_template_by_id(recordtemplate_id):
    with app.app_context():
        return RecordTemplate.query.options(
            db.joinedload(RecordTemplate.category),
            db.joinedload(RecordTemplate.account)
        ).get(recordtemplate_id)

#region u
def update_template(recordtemplate_id, data):
    with app.app_context():
        recordtemplate = RecordTemplate.query.get(recordtemplate_id)
        if recordtemplate:
            for key, value in data.items():
                setattr(recordtemplate, key, value)
            db.session.commit()
        return recordtemplate

#region d
def delete_template(recordtemplate_id):
    with app.app_context():
        recordtemplate = RecordTemplate.query.get(recordtemplate_id)
        if recordtemplate:
            db.session.delete(recordtemplate)
            db.session.commit()
            return True
        return False