from flask import Flask

from bagels.locations import database_file
from bagels.models.account import Account
from bagels.models.category import Category
from bagels.models.person import Person
from bagels.models.record import Record
from bagels.models.record_template import RecordTemplate
from bagels.models.split import Split

from .db import db


def create_app():
    """Create Flask app with dynamic database URI"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_file().resolve()}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

def _create_outside_source_account():
    outside_account = Account.query.filter_by(name="Outside source").first()
    if not outside_account:
        outside_account = Account(
            name="Outside source",
            description="Default account for external transactions",
            beginningBalance=0.0,
            hidden=True
        )
        db.session.add(outside_account)
        db.session.commit()

def init_db():
    # Recreate app to ensure latest database path is used
    global app
    app = create_app()
    with app.app_context():
        db.create_all()
        _create_outside_source_account()

def get_app():
    # Return current app instance with latest database path
    return app

def wipe_database():
    # Recreate app to ensure latest database path is used
    global app
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        _create_outside_source_account()