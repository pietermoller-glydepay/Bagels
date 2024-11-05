import copy

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static

from components.base import BasePage
from components.datatable import DataTable
from components.indicators import EmptyIndicator
from components.modals import ConfirmationModal, InputModal
from config import CONFIG
from queries.accounts import (create_account, delete_account,
                              get_account_by_id, get_all_accounts,
                              update_account)


class Page(Static):
    
    COLUMNS = ("Name", "Description", "Beginning Balance", "Repayment Date")
    
    # --------------- Hooks -------------- #
    
    def on_mount(self) -> None:
        self._build_table()
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key:
            self.current_row = event.row_key.value
    
    # -------------- Helpers ------------- #
    
    def _build_table(self) -> None:
        def get_table() -> DataTable:
            return self.query_one("#accounts-table")
        def get_empty_indicator() -> Static:
            return self.query_one("#empty-indicator")
        table = get_table()
        empty_indicator = get_empty_indicator()
        table.clear()
        if not table.columns:
            table.add_columns(*self.COLUMNS)
        accounts = get_all_accounts()
        if accounts:
            for account in accounts:
                table.add_row(account.name, account.description, account.beginningBalance, account.repaymentDate, key=str(account.id))
            table.focus()
        else:
            self.current_row = None
        empty_indicator.display = not accounts
    
    def _notify_no_accounts(self) -> None:
        self.app.notify(title="Error", message="Account must be selected for this action.", severity="error", timeout=2)
    
    # ------------- Callbacks ------------ #
    
    def action_new_account(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_account(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                self.app.notify(title="Success", message=f"Account {result['name']} created", severity="information", timeout=3)
                self._build_table()
        
        self.app.push_screen(InputModal("New Account", ACCOUNT_FORM), callback=check_result)

    def action_delete_account(self) -> None:
        def check_delete(result: bool) -> None:
            if result:
                delete_account(self.current_row)
                self.app.notify(title="Success", message=f"Deleted account", severity="information", timeout=3)
                self._build_table()
        if self.current_row:
            self.app.push_screen(ConfirmationModal("Are you sure you want to delete this account? Your existing transactions will not be deleted."), check_delete)
        else:
            self._notify_no_accounts()
    
    def action_edit_account(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    update_account(self.current_row, result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                self.app.notify(title="Success", message=f"Account {result['name']} updated", severity="information", timeout=3)
                self._build_table()
        
        if self.current_row:
            account = get_account_by_id(self.current_row)
            filled_account_form = copy.deepcopy(ACCOUNT_FORM)
            for field in filled_account_form:
                value = getattr(account, field["key"])
                field["defaultValue"] = str(value) if value is not None else ""
            self.app.push_screen(InputModal("Edit Account", filled_account_form), callback=check_result)
        else:
            self._notify_no_accounts()
    
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        self.basePage = BasePage(
            pageName="Accounts",
            bindings=[
                (CONFIG.hotkeys.new, "new_account", "Add", self.action_new_account), 
                (CONFIG.hotkeys.delete, "delete_account", "Delete", self.action_delete_account), 
                (CONFIG.hotkeys.edit, "edit_account", "Edit", self.action_edit_account), 
            ],
        )
        with self.basePage:
            yield DataTable(id="accounts-table", cursor_type="row", cursor_foreground_priority=True, zebra_stripes=True)
            yield EmptyIndicator("No accounts")

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
        "type": "integer",
    }
]