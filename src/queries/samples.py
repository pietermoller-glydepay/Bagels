from pathlib import Path

import yaml

from models.account import Account
from models.database.app import get_app
from models.database.db import db
from models.person import Person
from models.record import Record
from models.record_template import RecordTemplate
from models.split import Split
from queries.categories import create_default_categories

app = get_app()

def create_sample_entries():
    yaml_path = Path(__file__).parent.parent / "templates" / "sample_entries.yaml"
    
    with open(yaml_path, 'r') as file:
        sample_entries = yaml.safe_load(file)
    
    create_default_categories()

    with app.app_context():
        # Create accounts
        accounts = {}
        for account_data in sample_entries["accounts"]:
            account = Account(**account_data)
            db.session.add(account)
            db.session.flush()
            accounts[account.id] = account

        # Create people
        people = {}
        for person_data in sample_entries["people"]:
            person = Person(**person_data)
            db.session.add(person)
            db.session.flush()
            people[person.id] = person

        # Create records
        for record_data in sample_entries["records"]:
            # Handle splits if present
            splits_data = record_data.pop("splits", None)
            
            # Create record
            record = Record(**record_data)
            db.session.add(record)
            db.session.flush()

            # Create splits if any
            if splits_data:
                for split_data in splits_data:
                    split = Split(
                        recordId=record.id,
                        **split_data
                    )
                    db.session.add(split)

        # Create record templates
        for template_data in sample_entries["record_templates"]:
            template = RecordTemplate(**template_data)
            db.session.add(template)

        db.session.commit()