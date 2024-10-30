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

def init_db():
    with app.app_context():
        db.create_all()

def get_app():
    return app
