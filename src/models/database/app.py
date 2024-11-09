from flask import Flask

from models.account import Account
from models.category import Category
from models.person import Person
from models.record import Record
from models.split import Split

from .db import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./db.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

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
    with app.app_context():
        db.create_all()
        _create_outside_source_account()

def get_app():
    return app
