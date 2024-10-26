from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Label, Static

from components.base import BasePage
from components.modals import ConfirmationModal, InputModal
from controllers.categories import (create_category, create_default_categories,
                                    delete_category, get_all_categories)


class Page(Static):
    
    COLUMNS = ("", "Name", "Nature")
    
    # --------------- Hooks -------------- #
    
    def on_mount(self) -> None:
        self.build_table()
    
    def on_unmount(self) -> None:
        self.basePage.removeBinding("backspace")
    
    # ------------- Callbacks ------------ #
    
    def build_table(self) -> None:
        table = self.query_one("#categories-table")
        table.clear()
        if not table.columns:
            table.add_columns(*self.COLUMNS)
        categories = get_all_categories()
        if categories:
            self.basePage.newBinding("backspace", "delete_category", "Delete Category", self.action_delete_category)
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
                    self.mount(Label(f"[bold red]{e}[/bold red]"))
                self.build_table()
        
        # self.app.push_screen(InputModal(CATEGORY_FORM), callback=check_result)
        create_default_categories()
        self.build_table()

    def action_delete_category(self) -> None:
        def check_delete(result: bool) -> None:
            if result:
                delete_category(self.current_row)
                self.build_table()
        
        self.app.push_screen(ConfirmationModal("Are you sure you want to delete this record?"), check_delete)
    
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        self.basePage = BasePage(
            pageName="Categories",
            bindings=[
                ("ctrl+n", "new_category", "New Category", self.action_new_category), 
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
        "type": ["need", "want", "must"],
        "isRequired": True
    },
    {
        "title": "Color",
        "key": "color",
        "type": ["red", "orange", "yellow", "green", "blue", "purple"],
        "isRequired": False
    }
]