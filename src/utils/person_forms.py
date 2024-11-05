import copy

from queries.persons import get_person_by_id


class PersonForm:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------ Blueprints ------------ #

    FORM = [
            {
                "placeholder": "Steve",
                "title": "Name",
                "key": "name",
                "type": "string",
                "isRequired": True
            },
        ]
    # ------------- Builders ------------- #
    
    def get_filled_form(self, personId: int):
        form = copy.deepcopy(self.FORM)
        person = get_person_by_id(personId)
        for field in form:
            value = getattr(person, field["key"])
            field["defaultValue"] = str(value) if value is not None else ""
        return form
    
    def get_form(self):
        return copy.deepcopy(self.FORM)
