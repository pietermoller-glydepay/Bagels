from models.forms import RecordFormModel, SplitFormModel, FieldOption
from typing import List, Tuple, Optional
from datetime import datetime
from controllers.accounts import get_all_accounts_with_balance
from controllers.categories import get_all_categories_by_freq, get_all_categories_tree
from controllers.records import get_record_by_id, get_record_total_split_amount
from rich.text import Text
from controllers.persons import get_all_persons

class RecordForm:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, created_person_callback: Optional[callable] = None):
        self.form_model = RecordFormModel()
        self.split_form_model = SplitFormModel()
        self.created_person_callback = created_person_callback
        self._populate_form_options()

    def _populate_form_options(self) -> None:
        # Populate account options
        accounts = get_all_accounts_with_balance()
        account_options = [
            FieldOption(
                text=account.name,
                value=account.id,
                postfix=Text(f"{account.balance}", style="yellow")
            ) for account in accounts
        ]
        
        self.form_model.accountId.options = account_options
        if accounts:
            self.form_model.accountId.defaultValue = accounts[0].id
            self.form_model.accountId.defaultValueText = accounts[0].name

        # Populate category options
        categories = get_all_categories_by_freq()
        self.form_model.categoryId.options = [
            FieldOption(
                text=category.name,
                value=category.id,
                prefix=Text("●", style=category.color),
                postfix=Text(f"↪ {category.parentCategory.name}" if category.parentCategory else "", 
                           style=category.parentCategory.color) if category.parentCategory else None
            ) for category, _ in categories
        ]

        # Populate person options
        people = get_all_persons()
        self.split_form_model.personId.options = [
            FieldOption(text=person.name, value=person.id)
            for person in people
        ]
        self.split_form_model.personId.create_action = self._action_create_person
        
        # Set account options for split form
        self.split_form_model.accountId.options = [
            FieldOption(text=account.name, value=account.id)
            for account in accounts
        ]
    
    def _action_create_person(self) -> None:
        """Create a new person"""
        self.created_person_callback()

    def get_split_form(self, index: int, isPaid: bool = False) -> List[dict]:
        """Get a copy of the split form with indexed keys"""
        split_form = self.split_form_model.model_dump()
        result = []
        
        for key, field in split_form.items():
            field_copy = field.copy()
            field_copy["key"] = f"{key}-{index}"
            
            if key == "isPaid":
                field_copy["defaultValue"] = isPaid
            elif key == "accountId" and isPaid:
                field_copy["type"] = "autocomplete"
            elif key == "paidDate" and isPaid:
                field_copy["type"] = "dateAutoDay"
                field_copy["defaultValue"] = datetime.now().strftime("%d")
                
            result.append(field_copy)
            
        return result

    def get_filled_form(self, recordId: int) -> Tuple[List[dict], List[dict]]:
        """Get forms filled with record data"""
        record = get_record_by_id(recordId, populate_splits=True)
        form_data = self.form_model.model_dump()
        
        # Fill main form
        for key, field in form_data.items():
            value = getattr(record, key)
            
            if key == "amount":
                field["defaultValue"] = str(value - get_record_total_split_amount(recordId))
            elif key == "date":
                field["defaultValue"] = (
                    value.strftime("%d") 
                    if value.month == datetime.now().month 
                    else value.strftime("%d %m %y")
                )
            elif key in ("categoryId", "accountId"):
                related_obj = getattr(record, key.replace("Id", ""))
                field["defaultValue"] = related_obj.id
                field["defaultValueText"] = related_obj.name
            else:
                field["defaultValue"] = str(value) if value is not None else ""

        # Fill splits form
        splits_form = []
        for index, split in enumerate(record.splits):
            split_fields = self.get_split_form(index, split.isPaid)
            for field in split_fields:
                key = field["key"].split("-")[0]
                value = getattr(split, key)
                
                if key == "paidDate" and value:
                    field["defaultValue"] = (
                        value.strftime("%d")
                        if value.month == datetime.now().month
                        else value.strftime("%d %m %y")
                    )
                elif key in ("accountId", "personId"):
                    if related_obj := getattr(split, key.replace("Id", "")):
                        field["defaultValue"] = related_obj.id
                        field["defaultValueText"] = related_obj.name
                else:
                    field["defaultValue"] = str(value) if value is not None else ""
                    
                splits_form.append(field)
                
        return list(form_data.values()), splits_form

    def get_form(self) -> List[dict]:
        """Get the base form"""
        return list(self.form_model.model_dump().values())
