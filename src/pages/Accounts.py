import copy

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import DataTable, Label, Static

from components.base import BasePage
from components.modals import ConfirmationModal, InputModal
from constants.config import CONFIG
from controllers.accounts import (create_account, delete_account,
                                  get_account_by_id, get_all_accounts,
                                  update_account)


class Page(Static):
    
    COLUMNS = ("Name", "Description", "Beginning Balance", "Repayment Date")
    
    # --------------- Hooks -------------- #
    
    def on_mount(self) -> None:
        self.build_table()
    
    def on_unmount(self) -> None:
        self.basePage.removeBinding(CONFIG["hotkeys"]["delete"])
        self.basePage.removeBinding(CONFIG["hotkeys"]["edit"])
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key:
            self.current_row = event.row_key.value
        
    # ------------- Callbacks ------------ #
    
    def build_table(self) -> None:
        table = self.query_one("#accounts-table")
        table.clear()
        if not table.columns:
            table.add_columns(*self.COLUMNS)
        accounts = get_all_accounts()
        if accounts:
            self.basePage.newBinding(CONFIG["hotkeys"]["delete"], "delete_account", "Delete Account", self.action_delete_account)
            self.basePage.newBinding(CONFIG["hotkeys"]["edit"], "edit_account", "Edit Account", self.action_edit_account)
            for account in accounts:
                table.add_row(account.name, account.description, account.beginningBalance, account.repaymentDate, key=str(account.id))
        
        table.zebra_stripes = True
        table.focus()
    
    def action_new_account(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_account(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                self.app.notify(title="Success", message=f"Account {result['name']} created", severity="information", timeout=3)
                self.build_table()
        
        self.app.push_screen(InputModal("New Account", ACCOUNT_FORM), callback=check_result)

    def action_delete_account(self) -> None:
        def check_delete(result: bool) -> None:
            if result:
                delete_account(self.current_row)
                self.app.notify(title="Success", message=f"Deleted account", severity="information", timeout=3)
                self.build_table()
        
        self.app.push_screen(ConfirmationModal("Are you sure you want to delete this account? Your existing transactions will not be deleted."), check_delete)
    
    def action_edit_account(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    update_account(self.current_row, result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                self.app.notify(title="Success", message=f"Account {result['name']} updated", severity="information", timeout=3)
                self.build_table()
        
        account = get_account_by_id(self.current_row)
        if account:
            filled_account_form = copy.deepcopy(ACCOUNT_FORM)
            for field in filled_account_form:
                value = getattr(account, field["key"])
                field["defaultValue"] = str(value) if value is not None else ""
            self.app.push_screen(InputModal("Edit Account", filled_account_form), callback=check_result)
    
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        self.basePage = BasePage(
            pageName="Accounts",
            bindings=[
                (CONFIG["hotkeys"]["new"], "new_account", "New Account", self.action_new_account), 
            ],
        )
        with self.basePage:
            yield DataTable(id="accounts-table", cursor_type="row", cursor_foreground_priority=True)
            if not get_all_accounts():
                yield Label("No accounts. Use [bold yellow][^n][/bold yellow] to create one.", classes="label-empty")

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