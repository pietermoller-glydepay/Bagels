import copy

from bagels.queries.accounts import get_account_by_id


class AccountForm:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------ Blueprints ------------ #

    FORM = [
            {
                "placeholder": "My Account",
                "title": "Name",
                "key": "name",
                "type": "string",
                "isRequired": True
            },
            {
                "placeholder": "0000-0000-0000",
                "title": "Description",
                "key": "description",
                "type": "string",
            },
            {
                "placeholder": "0.00",
                "title": "Beginning Balance",
                "key": "beginningBalance",
                "type": "number",
                "defaultValue": "0",
                "isRequired": True
            },
            {
                "placeholder": "dd",
                "title": "Repayment Date",
                "key": "repaymentDate",
                "type": "integer",
            }
        ]
    # ------------- Builders ------------- #
    
    def get_filled_form(self, accountId: int):
        form = copy.deepcopy(self.FORM)
        account = get_account_by_id(accountId)
        for field in form:
            value = getattr(account, field["key"])
            field["defaultValue"] = str(value) if value is not None else ""
        return form
    
    def get_form(self):
        return copy.deepcopy(self.FORM)
