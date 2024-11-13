import copy
from datetime import datetime

from rich.text import Text

from bagels.constants import COLORS
from bagels.models.category import Nature
from bagels.queries.categories import get_category_by_id
from bagels.queries.record_templates import get_template_by_id


class CategoryForm:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    # ------------ Blueprints ------------ #

    FORM = [
        {
            "placeholder": "My Category",
            "title": "Name",
            "key": "name",
            "type": "string",
            "isRequired": True,
        },
        {
            "title": "Nature",
            "key": "nature",
            "type": "autocomplete",
            "options": [
                {
                    "text": "Must",
                    "value": Nature.MUST,
                    "prefix": Text("●", style="red"),
                },
                {
                    "text": "Need",
                    "value": Nature.NEED,
                    "prefix": Text("●", style="orange"),
                },
                {
                    "text": "Want",
                    "value": Nature.WANT,
                    "prefix": Text("●", style="green"),
                },
            ],
            "isRequired": True,
            "placeholder": "Select Nature",
        },
        {
            "title": "Color",
            "key": "color",
            "type": "autocomplete",
            "options": [
                {"value": color, "prefix": Text("●", style=color)} for color in COLORS
            ],
            "isRequired": True,
            "placeholder": "Select Color",
        },
    ]

    # ----------------- - ---------------- #

    # def __init__(self):
    # self._populate_form_options()

    # -------------- Helpers ------------- #

    # ------------- Builders ------------- #

    def get_subcategory_form(self, parent_id: int) -> list:
        subcategory_form = copy.deepcopy(self.FORM)
        subcategory_form.append(
            {
                "key": "parentCategoryId",
                "type": "hidden",
                "defaultValue": str(parent_id),
            }
        )
        return subcategory_form

    def get_filled_form(self, category_id: int) -> list:
        """Return a copy of the form with values from the record"""
        filled_form = copy.deepcopy(self.FORM)
        category = get_category_by_id(category_id)
        if category:
            for field in filled_form:
                value = getattr(category, field["key"])
                if field["key"] == "nature":
                    field["defaultValue"] = category.nature
                    field["defaultValueText"] = category.nature.value
                elif field["key"] == "color":
                    field["defaultValue"] = category.color
                    field["defaultValueText"] = category.color
                else:
                    field["defaultValue"] = str(value) if value is not None else ""

        return filled_form

    def get_form(self):
        """Return the base form with default values"""
        return self.FORM
