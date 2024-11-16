from sqlalchemy.orm import sessionmaker
from bagels.models.database.app import db_engine
from bagels.models.record_template import RecordTemplate
from sqlalchemy.orm import joinedload, sessionmaker

Session = sessionmaker(bind=db_engine)


# region c
def create_template(data):
    session = Session()
    try:
        new_template = RecordTemplate(**data)
        session.add(new_template)
        session.commit()
        session.refresh(new_template)
        session.expunge(new_template)
        return new_template
    finally:
        session.close()


# region r
def get_all_templates():
    session = Session()
    try:
        return (
            session.query(RecordTemplate)
            .options(
                joinedload(RecordTemplate.category),
                joinedload(RecordTemplate.account),
            )
            .order_by(RecordTemplate.order)
            .all()
        )
    finally:
        session.close()


def get_template_by_id(recordtemplate_id):
    session = Session()
    try:
        return (
            session.query(RecordTemplate)
            .options(
                joinedload(RecordTemplate.category),
                joinedload(RecordTemplate.account),
            )
            .get(recordtemplate_id)
        )
    finally:
        session.close()


def get_adjacent_template(recordtemplate_id, direction):
    session = Session()
    try:
        recordtemplate = session.query(RecordTemplate).get(recordtemplate_id)
        if not recordtemplate:
            return -1

        current_order = recordtemplate.order
        if direction == "next":
            adjacent_template = (
                session.query(RecordTemplate)
                .filter(RecordTemplate.order == current_order + 1)
                .first()
            )
        else:  # direction == "previous"
            adjacent_template = (
                session.query(RecordTemplate)
                .filter(RecordTemplate.order == current_order - 1)
                .first()
            )

        if adjacent_template:
            return adjacent_template.id
        return -1
    finally:
        session.close()


# region u
def update_template(recordtemplate_id, data):
    session = Session()
    try:
        recordtemplate = session.query(RecordTemplate).get(recordtemplate_id)
        if recordtemplate:
            for key, value in data.items():
                setattr(recordtemplate, key, value)
            session.commit()
        return recordtemplate
    finally:
        session.close()


def swap_template_order(recordtemplate_id, direction="next"):
    session = Session()
    try:
        recordtemplate = session.query(RecordTemplate).get(recordtemplate_id)

        if recordtemplate:
            current_order = recordtemplate.order
            if direction == "next":
                swap_template = (
                    session.query(RecordTemplate)
                    .filter(RecordTemplate.order == current_order + 1)
                    .first()
                )
            else:  # direction == "previous"
                swap_template = (
                    session.query(RecordTemplate)
                    .filter(RecordTemplate.order == current_order - 1)
                    .first()
                )

            if swap_template:
                recordtemplate.order, swap_template.order = (
                    swap_template.order,
                    recordtemplate.order,
                )
                session.commit()
        return recordtemplate
    finally:
        session.close()


# region d
def delete_template(recordtemplate_id):
    session = Session()
    try:
        recordtemplate = session.query(RecordTemplate).get(recordtemplate_id)
        if recordtemplate:
            session.delete(recordtemplate)
            session.commit()
            return True
        return False
    finally:
        session.close()
