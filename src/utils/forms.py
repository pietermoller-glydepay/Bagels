import copy
from datetime import datetime

from rich.text import Text

from controllers.accounts import get_all_accounts_with_balance
from controllers.categories import get_all_categories_by_freq
from controllers.persons import create_person, get_all_persons
from controllers.records import get_record_by_id


class RecordForm:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------ Blueprints ------------ #

    FORM = [
        {
            "placeholder": "Label",
            "title": "Label", 
            "key": "label",
            "type": "string",
        },
        {
            "title": "Category",
            "key": "categoryId",
            "type": "autocomplete",
            "options": [],
            "isRequired": True,
            "placeholder": "Select Category"
        },
        {
            "placeholder": "0.00",
            "title": "Amount",
            "key": "amount",
            "type": "number",
            "min": 0,
            "isRequired": True,
        },
        {
            "title": "Account",
            "key": "accountId", 
            "type": "autocomplete",
            "options": [],
            "isRequired": True,
            "placeholder": "Select Account"
        },
        {
            "title": "Type",
            "key": "isIncome",
            "type": "boolean",
            "labels": ["Expense", "Income"],
            "defaultValue": False,
        },
        {
            "placeholder": "dd (mm) (yy)",
            "title": "Date",
            "key": "date",
            "type": "dateAutoDay",
            "defaultValue": datetime.now().strftime("%d")
        }
    ]
    
    SPLIT_FORM = [
            {   
                "title": "Person",
                "key": "personId", 
                "type": "autocomplete",
                "options":[],
                "create_action": None,
                "isRequired": True,
                "placeholder": "Select Person"
            },
            {
                "title": "Amount",
                "key": "amount",
                "type": "number", 
                "min": 0,
                "isRequired": True,
                "placeholder": "0.00"
            },
            {
                "title": "Paid",
                "key": "isPaid",
                "type": "hidden",
                "defaultValue": "False"
            },
            {
                "title": "Paid to account",
                "key": "accountId",
                "type": "hidden",
                "options": [],
                "placeholder": "Select Account"
            }
        ]
    
    # ----------------- - ---------------- #
    
    def __init__(self):
        self._populate_form_options()
        
    # -------------- Helpers ------------- #

    def _populate_form_options(self):
        accounts = get_all_accounts_with_balance()   
        self.FORM[3]["options"] = [
            {
                "text": account.name,
                "value": account.id,
                "postfix": Text(f"{account.balance}", style="yellow")
            }
            for account in accounts
        ]
        if accounts:
            self.FORM[3]["defaultValue"] = accounts[0].id
            self.FORM[3]["defaultValueText"] = accounts[0].name

        categories = get_all_categories_by_freq()
        self.FORM[1]["options"] = [
            {
                "text": category.name,
                "value": category.id,
                "prefix": Text("●", style=category.color),
                "postfix": Text(f"↪ {category.parentCategory.name}" if category.parentCategory else "", style=category.parentCategory.color) if category.parentCategory else ""
            }
            for category, _ in categories
        ]
        people = get_all_persons()
        self.SPLIT_FORM[0]["options"] = [
            {"text": person.name, "value": person.id} for person in people
        ]
        self.SPLIT_FORM[0]["create_action"] = self._action_create_person
        self.SPLIT_FORM[3]["options"] = [
            {"text": account.name, "value": account.id} for account in accounts
        ]
        
    # ------------- Functions ------------ #
    
    def _action_create_person(self, name: str):
        create_person(name)
        self._populate_form_options()
    
    # ------------- Builders ------------- #
    
    def get_split_form(self, index: int, isPaid: bool = False):
        split_form = copy.deepcopy(self.SPLIT_FORM)
        for field in split_form:
            fieldKey = field["key"]
            field["key"] = f"{fieldKey}-{index}"
            if fieldKey == "isPaid":
                field["defaultValue"] = str(isPaid)
            elif fieldKey == "accountId" and isPaid:
                field["type"] = "autocomplete"
        return split_form

    def get_filled_form(self, recordId):
        """Return a copy of the form with values from the record"""
        filled_form = copy.deepcopy(self.FORM)
        record = get_record_by_id(recordId, populate_splits=True)
        for field in filled_form:
            fieldKey = field["key"]
            value = getattr(record, fieldKey) # gets the value of the field from the record
            if fieldKey == "date":
                field["defaultValue"] = value.strftime("%d")
            elif fieldKey == "isIncome":
                field["defaultValue"] = value
            elif fieldKey == "categoryId":
                field["defaultValue"] = record.category.id
                field["defaultValueText"] = record.category.name
            elif fieldKey == "accountId":
                field["defaultValue"] = record.account.id
                field["defaultValueText"] = record.account.name
            else:
                field["defaultValue"] = str(value) if value is not None else ""
        for index, split in enumerate(record.splits):
            split_form = self.get_split_form(index, split.isPaid)
            for field in split_form:
                fieldKey = field["key"]
                value = getattr(split, fieldKey)
                if fieldKey == "accountId":
                    field["defaultValue"] = split.account.id
                    field["defaultValueText"] = split.account.name
                elif fieldKey == "personId":
                    field["defaultValue"] = split.person.id
                    field["defaultValueText"] = split.person.name
                else:
                    field["defaultValue"] = str(value) if value is not None else ""
                filled_form.append(field)
        return filled_form

    def get_form(self):
        """Return the base form"""
        return self.FORM
