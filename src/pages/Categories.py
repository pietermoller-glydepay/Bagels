import copy

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Label, Select, Static

from components.base import BasePage
from components.indicators import EmptyIndicator
from components.modals import ConfirmationModal, InputModal
from constants.config import CONFIG
from controllers.categories import (create_category, create_default_categories,
                                    delete_category, get_all_categories_tree,
                                    get_category_by_id, update_category)
from models.category import Nature


class Page(Static):
    
    COLUMNS = ("", "Name", "Nature")
    
    # --------------- Hooks -------------- #
    
    def on_mount(self) -> None:
        self._build_table()
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key:
            self.current_row = event.row_key.value
        
    # -------------- Helpers ------------- #
    
    def _build_table(self) -> None:
        def get_table() -> DataTable:
            return self.query_one("#categories-table")
        def get_empty_indicator() -> Static:
            return self.query_one("#empty-indicator")
        table = get_table()
        table.clear()
        if not table.columns:
            table.add_columns(*self.COLUMNS)
        categories = get_all_categories_tree()
        if categories:
            for category, node in categories:
                table.add_row(node, category.name, category.nature.value, key=category.id)
            table.zebra_stripes = True
            table.focus()
        else:
            empty_indicator = get_empty_indicator()
            self.current_row = None
        empty_indicator.display = not categories
    
    def _notify_no_categories(self) -> None:
        self.app.notify(title="Error", message="Category must be selected for this action.", severity="error", timeout=2)
        
    # ------------- Callbacks ------------ #
    
    def action_new_category(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_category(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:
                    self.app.notify(title="Success", message=f"Category created", severity="information", timeout=3)
                    self._build_table()
        
        self.app.push_screen(InputModal("New Category", CATEGORY_FORM), callback=check_result)
    
    def action_new_subcategory(self) -> None:
        if not self.current_row:
            self._notify_no_categories()
            return

        def check_result(result: bool) -> None:
            if result:
                try:
                    create_category(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:
                    self.app.notify(title="Success", message=f"Subcategory created", severity="information", timeout=3)
                    self._build_table()

        subcategory_form = copy.deepcopy(CATEGORY_FORM)
        subcategory_form.append({
            "key": "parentCategoryId",
            "type": "hidden",
            "defaultValue": str(self.current_row)
        })
        parent_category = get_category_by_id(self.current_row)
        self.app.push_screen(InputModal(f"New Subcategory of {parent_category.name}", subcategory_form), callback=check_result)

    def action_delete_category(self) -> None:
        if not self.current_row:
            self._notify_no_categories()
            return

        def check_delete(result: bool) -> None:
            if result:
                try:
                    delete_category(self.current_row)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                self._build_table()
        
        self.app.push_screen(ConfirmationModal("Are you sure you want to delete this record?"), check_delete)
        
    def action_edit_category(self) -> None:
        if not self.current_row:
            self._notify_no_categories()
            return

        def check_result(result: bool) -> None:
            if result:
                try:
                    update_category(self.current_row, result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:
                    self.app.notify(title="Success", message=f"Category {result['name']} updated", severity="information", timeout=3)
                    self._build_table()
        
        category = get_category_by_id(self.current_row)
        filled_category_form = copy.deepcopy(CATEGORY_FORM)
        if category:
            for field in filled_category_form:
                value = getattr(category, field["key"])
                if field["key"] == "nature":
                    field["defaultValue"] = category.nature
                    field["defaultValueText"] = category.nature.value
                elif field["key"] == "color":
                    field["defaultValue"] = category.color
                    field["defaultValueText"] = category.color
                else:
                    field["defaultValue"] = str(value) if value is not None else ""
            self.app.push_screen(InputModal("Edit Category", filled_category_form), callback=check_result)
    
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        self.basePage = BasePage(
            pageName="Categories",
            bindings=[
                (CONFIG["hotkeys"]["new"], "new_category", "Add", self.action_new_category),
                (CONFIG["hotkeys"]["categories"]["new_subcategory"], "new_subcategory", "Add Subcategory", self.action_new_subcategory),
                (CONFIG["hotkeys"]["edit"], "edit_category", "Edit", self.action_edit_category),
                (CONFIG["hotkeys"]["delete"], "delete_category", "Delete", self.action_delete_category),
            ],
        )
        with self.basePage:
            yield DataTable(id="categories-table", cursor_type="row", cursor_foreground_priority=True)
            yield EmptyIndicator("No categories")

CATEGORY_FORM = [
    {
        "placeholder": "My Category",
        "title": "Name",
        "key": "name",
        "type": "string",
        "isRequired": True
    },
    {
        "title": "Nature",
        "key": "nature",
        "type": "autocomplete",
        "options": [
            {
                "text": "Must",
                "value": Nature.MUST,
                "prefix": Text("●", style="red")
            },
            {
                "text": "Need",
                "value": Nature.NEED,
                "prefix": Text("●", style="orange")
            },
            {
                "text": "Want",
                "value": Nature.WANT,
                "prefix": Text("●", style="green")
            }
        ],
        "isRequired": True,
        "placeholder": "Select Nature"
    },
    {
        "title": "Color",
        "key": "color",
        "type": "autocomplete",
        "options": [
            {
                "value": "Red",
                "prefix": Text("●", style="red")
            },
            {
                "value": "Orange",
                "prefix": Text("●", style="orange")
            },
            {
                "value": "Yellow",
                "prefix": Text("●", style="yellow")
            },
            {
                "value": "Green",
                "prefix": Text("●", style="green")
            },
            {
                "value": "Blue",
                "prefix": Text("●", style="blue")
            },
            {
                "value": "Purple",
                "prefix": Text("●", style="purple")
            },
            {
                "value": "Grey",
                "prefix": Text("●", style="grey")
            },
            {
                "value": "White",
                "prefix": Text("●", style="white")
            }
        ],
        "isRequired": True,
        "placeholder": "Select Color"
    }
]