import copy

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Label, Select, Static

from components.base import BasePage
from components.modals import ConfirmationModal, InputModal
from controllers.categories import (create_category, create_default_categories,
                                    delete_category, get_all_categories,
                                    get_category_by_id, update_category)
from models.category import Nature


class Page(Static):
    
    COLUMNS = ("", "Name", "Nature")
    
    # --------------- Hooks -------------- #
    
    def on_mount(self) -> None:
        self.build_table()
    
    def on_unmount(self) -> None:
        self.basePage.removeBinding("backspace")
        self.basePage.removeBinding("ctrl+d")
        self.basePage.removeBinding("ctrl+e")
        
    # ------------- Callbacks ------------ #
    
    def build_table(self) -> None:
        table = self.query_one("#categories-table")
        table.clear()
        if not table.columns:
            table.add_columns(*self.COLUMNS)
        categories = get_all_categories()
        if categories:
            self.basePage.newBinding("ctrl+d", "new_subcategory", "New Subcategory", self.action_new_subcategory)
            self.basePage.newBinding("ctrl+e", "edit_category", "Edit", self.action_edit_category)
            self.basePage.newBinding("backspace", "delete_category", "Delete", self.action_delete_category)
            for category, node in categories:
                table.add_row(node, category.name, category.nature.value, key=category.id)
        
        table.zebra_stripes = True
        table.focus()
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key:
            self.current_row = event.row_key.value
    
    def action_new_category(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_category(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                self.build_table()
        
        self.app.push_screen(InputModal("New Category", CATEGORY_FORM), callback=check_result)
    
    def action_new_subcategory(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_category(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                self.build_table()
        subcategory_form = copy.deepcopy(CATEGORY_FORM)
        subcategory_form.append({
            "key": "parentCategoryId",
            "type": "hidden",
            "defaultValue": self.current_row
        })
        parent_category = get_category_by_id(self.current_row)
        self.app.push_screen(InputModal(f"New Subcategory of {parent_category.name}", subcategory_form), callback=check_result)

    def action_delete_category(self) -> None:
        def check_delete(result: bool) -> None:
            if result:
                try:
                    delete_category(self.current_row)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                self.build_table()
        
        self.app.push_screen(ConfirmationModal("Are you sure you want to delete this record?"), check_delete)
        
    def action_edit_category(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    update_category(self.current_row, result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:
                    self.app.notify(title="Success", message=f"Category {result['name']} updated", severity="information", timeout=3)
                    self.build_table()
        
        category = get_category_by_id(self.current_row)
        if category:
            filled_category_form = [
                {**field, "defaultValue": getattr(category, field["key"], "")}
                for field in CATEGORY_FORM
            ]
            self.app.push_screen(InputModal("Edit Category", filled_category_form), callback=check_result)
    
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        self.basePage = BasePage(
            pageName="Categories",
            bindings=[
                ("ctrl+n", "new_category", "New", self.action_new_category), 
            ],
        )
        with self.basePage:
            yield DataTable(id="categories-table", cursor_type="row")

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
                "value": "red",
                "prefix": Text("●", style="red")
            },
            {
                "value": "orange",
                "prefix": Text("●", style="orange")
            },
            {
                "value": "yellow",
                "prefix": Text("●", style="yellow")
            },
            {
                "value": "green",
                "prefix": Text("●", style="green")
            },
            {
                "value": "blue",
                "prefix": Text("●", style="blue")
            },
            {
                "value": "purple",
                "prefix": Text("●", style="purple")
            },
            {
                "value": "grey",
                "prefix": Text("●", style="grey")
            },
            {
                "value": "white",
                "prefix": Text("●", style="white")
            }
        ],
        "isRequired": True,
        "placeholder": "Select Color"
    }
]