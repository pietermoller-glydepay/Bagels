import copy
from datetime import datetime

from rich.text import Text

from bagels.queries.accounts import get_all_accounts_with_balance
from bagels.queries.categories import get_all_categories_by_freq
from bagels.queries.record_templates import get_template_by_id


class RecordTemplateForm:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------ Blueprints ------------ #

    FORM = [
        {
            "placeholder": "Template label",
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
        
    # ------------- Builders ------------- #

    def get_filled_form(self, templateId: int) -> list:
        """Return a copy of the form with values from the record"""
        filled_form = copy.deepcopy(self.FORM)
        template = get_template_by_id(templateId)
        
        for field in filled_form:
            fieldKey = field["key"]
            value = getattr(template, fieldKey)
            
            match fieldKey:
                case "isIncome":
                    field["defaultValue"] = value
                case "categoryId":
                    field["defaultValue"] = template.category.id
                    field["defaultValueText"] = template.category.name
                case "accountId":
                    field["defaultValue"] = template.account.id
                    field["defaultValueText"] = template.account.name
                case _:
                    field["defaultValue"] = str(value) if value is not None else ""
                
        return filled_form
    
    def get_form(self):
        """Return the base form with default values"""
        form = copy.deepcopy(self.FORM)
        return form
