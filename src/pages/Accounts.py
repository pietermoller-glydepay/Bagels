from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Label, Static

from components.base import BasePage
from components.modals import ConfirmationModal, InputModal
from controllers.accounts import (create_account, delete_account,
                                  get_all_accounts)


class Page(Static):
    
    COLUMNS = ("Name", "Description", "Beginning Balance", "Repayment Date")
    
    # --------------- Hooks -------------- #
    
    def on_mount(self) -> None:
        self.build_table()
    
    def on_unmount(self) -> None:
        self.basePage.removeBinding("backspace")
    
    # ------------- Callbacks ------------ #
    
    def build_table(self) -> None:
        table = self.query_one("#accounts-table")
        table.clear()
        if not table.columns:
            table.add_columns(*self.COLUMNS)
        accounts = get_all_accounts()
        if accounts:
            self.basePage.newBinding("backspace", "delete_account", "Delete Account", self.action_delete_account)
            for account in accounts:
                table.add_row(account.name, account.description, account.beginningBalance, account.repaymentDate, key=str(account.id))
        
        table.zebra_stripes = True
        table.focus()
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key:
            self.current_row = event.row_key.value
    
    def action_new_account(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_account(result)
                except Exception as e:
                    self.mount(Label(f"[bold red]{e}[/bold red]"))
                self.build_table()
        
        self.app.push_screen(InputModal(ACCOUNT_FORM), callback=check_result)

    def action_delete_account(self) -> None:
        def check_delete(result: bool) -> None:
            if result:
                delete_account(self.current_row)
                self.build_table()
        
        self.app.push_screen(ConfirmationModal("Are you sure you want to delete this record?"), check_delete)
    
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        self.basePage = BasePage(
            pageName="Accounts",
            bindings=[
                ("ctrl+n", "new_account", "New Account", self.action_new_account), 
            ],
        )
        with self.basePage:
            yield DataTable(id="accounts-table", cursor_type="row")

ACCOUNT_FORM = [
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
        "type": "number",
    }
]