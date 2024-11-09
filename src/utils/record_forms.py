import copy
from datetime import datetime

from rich.text import Text

from components.autocomplete import Dropdown
from queries.accounts import get_all_accounts_with_balance
from queries.categories import get_all_categories_by_freq
from queries.persons import create_person, get_all_persons
from queries.records import get_record_by_id, get_record_total_split_amount


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
            "isRequired": True,
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
                "create_action": True,
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
                "defaultValue": False
            },
            {
                "title": "Paid to account",
                "key": "accountId",
                "type": "hidden",
                "options": [],
                "placeholder": "Select Account",
            },
            {
                "title": "Paid Date",
                "key": "paidDate",
                "type": "hidden",
                "defaultValue": None
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
        self.SPLIT_FORM[3]["options"] = [
            {"text": account.name, "value": account.id} for account in accounts
        ]
    
    # ------------- Builders ------------- #
    
    def get_split_form(self, index: int, isPaid: bool = False):
        split_form = copy.deepcopy(self.SPLIT_FORM)
        for field in split_form:
            fieldKey = field["key"]
            field["key"] = f"{fieldKey}-{index}"
            if fieldKey == "isPaid":
                field["defaultValue"] = isPaid
            elif fieldKey == "accountId" and isPaid:
                field["type"] = "autocomplete"
            elif fieldKey == "paidDate" and isPaid:
                field["type"] = "dateAutoDay"
                field["defaultValue"] = datetime.now().strftime("%d")
        return split_form

    def get_filled_form(self, recordId: int) -> tuple[list, list]:
        """Return a copy of the form with values from the record"""
        filled_form = copy.deepcopy(self.FORM)
        record = get_record_by_id(recordId, populate_splits=True)
        
        for field in filled_form:
            fieldKey = field["key"]
            value = getattr(record, fieldKey)
            
            match fieldKey:
                case "amount":
                    field["defaultValue"] = str(value - get_record_total_split_amount(recordId))
                case "date":
                    # if value is this month, simply set %d, else set %d %m %y
                    if value.month == datetime.now().month:
                        field["defaultValue"] = value.strftime("%d")
                    else:
                        field["defaultValue"] = value.strftime("%d %m %y")
                case "isIncome":
                    field["defaultValue"] = value
                case "categoryId":
                    field["defaultValue"] = record.category.id
                    field["defaultValueText"] = record.category.name
                case "accountId":
                    field["defaultValue"] = record.account.id
                    field["defaultValueText"] = record.account.name
                case _:
                    field["defaultValue"] = str(value) if value is not None else ""
        
        filled_splits = []
        for index, split in enumerate(record.splits):
            split_form = self.get_split_form(index, split.isPaid)
            for field in split_form:
                fieldKey = field["key"].split("-")[0]
                value = getattr(split, fieldKey)
                
                match fieldKey:
                    case "paidDate":
                        if value:
                            if value.month == datetime.now().month:
                                field["defaultValue"] = value.strftime("%d")
                            else:
                                field["defaultValue"] = value.strftime("%d %m %y")
                    case "accountId":
                        if split.account:
                            field["defaultValue"] = split.account.id
                            field["defaultValueText"] = split.account.name
                    case "personId":
                        field["defaultValue"] = split.person.id
                        field["defaultValueText"] = split.person.name
                    case "isPaid":
                        field["defaultValue"] = split.isPaid
                    case _:
                        field["defaultValue"] = str(value) if value is not None else ""
                        
                filled_splits.append(field)
                
        return filled_form, filled_splits
    
    def get_form(self, hidden_fields: dict = {}):
        """Return the base form with default values"""
        form = copy.deepcopy(self.FORM)
        for field in form:
            key = field["key"]
            if key in hidden_fields:
                field["type"] = "hidden"
                if isinstance(hidden_fields[key], dict):
                    field["defaultValue"] = hidden_fields[key]["defaultValue"]
                    field["defaultValueText"] = hidden_fields[key]["defaultValueText"]
                else:
                    field["defaultValue"] = hidden_fields[key]
        return form
