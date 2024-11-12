from flask import Flask
from flask_migrate import Migrate

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
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{database_file().resolve()}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)
    return app


def _create_outside_source_account():
    outside_account = Account.query.filter_by(name="Outside source").first()
    if not outside_account:
        outside_account = Account(
            name="Outside source",
            description="Default account for external transactions",
            beginningBalance=0.0,
            hidden=True,
        )
        db.session.add(outside_account)
        db.session.commit()


def _sync_database_schema(app):
    """Attempt to automatically sync database schema"""
    try:
        with app.app_context():
            # Get all existing tables
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()

            # Create tables that don't exist
            for table in db.Model.metadata.tables.values():
                if table.name not in existing_tables:
                    table.create(db.engine)
                else:
                    # Get existing columns
                    existing_columns = {
                        col["name"] for col in inspector.get_columns(table.name)
                    }
                    # Get model columns
                    model_columns = {col.name for col in table.columns}

                    # Add missing columns
                    for column_name in model_columns - existing_columns:
                        column = table.columns[column_name]
                        # Create new column with nullable=True to handle existing rows
                        with db.engine.connect() as conn:
                            conn.execute(
                                db.text(
                                    f'ALTER TABLE {table.name} ADD COLUMN "{column_name}" {column.type}'
                                )
                            )
                            conn.commit()

    except Exception as e:
        raise Exception(f"Failed to sync database schema: {str(e)}")


def init_db():
    # Recreate app to ensure latest database path is used
    global app
    app = create_app()
    with app.app_context():
        _sync_database_schema(app)
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
        _sync_database_schema(app)
        db.create_all()
        _create_outside_source_account()
