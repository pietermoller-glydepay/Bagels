from datetime import datetime

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Checkbox, DataTable, Label, Rule, Static

from components.base import BasePage
from components.modals import ConfirmationModal, InputModal
from controllers.accounts import get_all_accounts_with_balance


class Page(Static):
    def on_mount(self) -> None:
        self.build_table()

    # ------------- Callbacks ------------ #
    
    def build_table(self) -> None:
        table = self.query_one("#records-table")
        table.clear()
        if not table.columns:
            table.add_columns("T", "Date", "Category", "Amount", "Label")
        # table.add_rows(get_record_table_rows())
        table.cursor_type = 'cell'
        table.zebra_stripes = True
        table.focus()
    
    def action_new_records(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                pass
        
        self.app.push_screen(InputModal(RECORD_FORM), callback=check_result)
        pass

    def action_delete_record(self) -> None:
        def check_delete(result: bool) -> None:
            if result:
                self.mount(Label("Deleted"))
        
        self.app.push_screen(ConfirmationModal("Are you sure you want to delete this record?"), check_delete)

    # --------------- View --------------- #
    
    def compose(self) -> ComposeResult:
        self.basepage = BasePage(
            pageName="Home",
            bindings=[
                ("ctrl+n", "new_records", "New Records", self.action_new_records), 
            ],
        )
        with self.basepage:
            with Horizontal(classes="home-accounts-list"):
                for account in get_all_accounts_with_balance():
                    with Container(classes="account-container"):
                        yield Label(f"[bold]{account['name']}[/bold][italic] {account['description']}[/italic]", classes="account-name", markup=True)
                        yield Label(f"${account['balance']}", classes="account-balance")
            yield Rule(classes="home-divider", line_style="double")
            yield DataTable(id="records-table")

RECORD_FORM = [
    {
        "placeholder": "Label",
        "title": "Label",
        "key": "label",
        "type": "string",
    },
    {
        "placeholder": "0.00",
        "title": "Amount",
        "key": "amount",
        "type": "number",
    },
    {
        "placeholder": "dd (mm) (yy)",
        "title": "Date",
        "key": "date",
        "type": "dateAutoDay",
        "defaultValue": datetime.now().strftime("%d")
    },
]