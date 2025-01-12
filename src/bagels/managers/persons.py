from sqlalchemy import and_, select
from sqlalchemy.orm import contains_eager, sessionmaker

from bagels.managers.utils import get_operator_amount, get_start_end_of_period
from bagels.models.category import Category
from bagels.models.database.app import db_engine
from bagels.models.person import Person
from bagels.models.record import Record
from bagels.models.split import Split

Session = sessionmaker(bind=db_engine)


def create_person(data):
    """Create a new person entry in the database."""
    session = Session()
    try:
        new_person = Person(**data)
        session.add(new_person)
        session.commit()
        session.refresh(new_person)
        session.expunge(new_person)
        return new_person
    finally:
        session.close()


def get_all_persons():
    """Retrieve all persons from the database."""
    session = Session()
    try:
        return session.scalars(select(Person)).all()
    finally:
        session.close()


def get_person_by_id(person_id):
    """Retrieve a person by their ID."""
    session = Session()
    try:
        return session.get(Person, person_id)
    finally:
        session.close()


def update_person(person_id, data):
    """Update a person's information by their ID."""
    session = Session()
    try:
        person = session.get(Person, person_id)
        if person:
            for key, value in data.items():
                setattr(person, key, value)
            session.commit()
            session.refresh(person)
            session.expunge(person)
        return person
    finally:
        session.close()


def delete_person(person_id):
    """Delete a person from the database by their ID."""
    session = Session()
    try:
        person = session.get(Person, person_id)
        if person:
            session.delete(person)
            session.commit()
            return True
        return False
    finally:
        session.close()


def get_persons_with_splits(
    offset: int = 0,
    offset_type: str = "month",
    category_piped_names: str = None,
    operator_amount: str = None,
    label: str = None,
):
    """Get all persons with their splits for the specified period."""
    session = Session()
    try:
        start_of_period, end_of_period = get_start_end_of_period(offset, offset_type)

        # Build the base query
        stmt = (
            select(Person)
            .options(
                contains_eager(Person.splits)
                .contains_eager(Split.record)
                .contains_eager(Record.category),
                contains_eager(Person.splits).contains_eager(Split.account),
            )
            .join(Person.splits)
            .join(Split.record)
            .outerjoin(Record.category)
            .outerjoin(Split.account)
        )

        # Apply date filter
        stmt = stmt.filter(
            and_(Record.date >= start_of_period, Record.date < end_of_period)
        )

        # Apply category filter
        if category_piped_names not in [None, ""]:
            category_names = category_piped_names.split("|")
            stmt = stmt.filter(Category.name.in_(category_names))

        # Apply amount filter
        if operator_amount not in [None, ""]:
            operator, amount = get_operator_amount(operator_amount)
            if operator and amount:
                stmt = stmt.filter(Split.amount.op(operator)(amount))

        # Apply label filter
        if label not in [None, ""]:
            stmt = stmt.filter(Record.label.ilike(f"%{label}%"))

        # Apply ordering and distinct
        stmt = stmt.order_by(Record.date.asc()).distinct()

        result = session.scalars(stmt)
        return result.unique().all()
    finally:
        session.close()
