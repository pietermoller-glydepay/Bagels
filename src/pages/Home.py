import copy
from datetime import datetime

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Checkbox, DataTable, Label, Rule, Static

from components.base import BasePage
from components.modals import (ConfirmationModal, InputModal, RecordModal,
                               TransferModal)
from constants.config import CONFIG
from controllers.accounts import (get_account_balance_by_id,
                                  get_accounts_count, get_all_accounts,
                                  get_all_accounts_with_balance)
from controllers.categories import (get_all_categories_by_freq,
                                    get_all_categories_tree,
                                    get_categories_count)
from controllers.records import (create_record, delete_record,
                                 get_record_by_id, get_records, update_record)
from controllers.splits import create_split, delete_splits_by_record_id
from utils.format import format_date_to_readable
from utils.forms import RecordForm


class Page(Static):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def on_mount(self) -> None:
        self.record_form = RecordForm()
        self.build_table()
        if get_accounts_count() > 1:
            self.basePage.newBinding("ctrl+t", "new_transfer", "Transfer", self.action_new_transfer)
    
    def on_unmount(self) -> None:
        self.basePage.removeBinding(CONFIG["hotkeys"]["delete"])
        self.basePage.removeBinding(CONFIG["hotkeys"]["edit"])
        self.basePage.removeBinding("ctrl+t")
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key:
            self.current_row = event.row_key.value

    # ------------- Callbacks ------------ #
    
    def build_table(self) -> None:
        def get_table() -> DataTable:
            return self.query_one("#records-table")
        table = get_table()
        table.clear()
        if not table.columns:
            table.add_columns(" ", "Date", "Category", "Amount", "Label")
        records = get_records()
        if records: 
            self.basePage.newBinding(CONFIG["hotkeys"]["delete"], "delete_record", "Delete", self.action_delete_record)
            self.basePage.newBinding(CONFIG["hotkeys"]["edit"], "edit_record", "Edit", self.action_edit_record)
            for record in records:
                flow_icon = "[green]+[/green]" if record.isIncome else "[red]-[/red]"
                type_icon = " "
                if record.isTransfer:
                    category_string = record.account.name + " → " + record.transferToAccount.name
                    amount_string = record.amount
                else:
                    color_tag = record.category.color.lower()
                    category_string = f"[{color_tag}]●[/{color_tag}] {record.category.name}"
                    amount_string = f"{flow_icon} {record.amount}"
                table.add_row(
                    type_icon,
                    format_date_to_readable(record.date),
                    category_string,
                    amount_string,
                    record.label,
                    key=str(record.id),
                )
        table.focus()
        
    def update_account_balance(self, account_id: int) -> None:
        self.query_one(f"#account-{account_id}-balance").update(f"${get_account_balance_by_id(account_id)}")
    
    def action_new_record(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    pass
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:   
                    self.app.notify(title="Success", message=f"Record created", severity="information", timeout=3)
                    self.update_account_balance(result['accountId'])
                    self.build_table()
        
        self.app.push_screen(RecordModal("New Record", self.record_form.get_form()), callback=check_result)
    
    def action_edit_record(self) -> None:
        record = get_record_by_id(self.current_row)
        def check_result(result: bool) -> None:
            if result:
                try:
                    pass
                        
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:
                    self.app.notify(title="Success", message=f"Record updated", severity="information", timeout=3)
                    self.update_account_balance(result['accountId'])
                    if record.isTransfer:
                        self.update_account_balance(result['transferToAccountId'])
                    self.build_table()
            else:
                self.app.notify(title="Discarded", message=f"Record not updated", severity="warning", timeout=3)
        
        if record:
            if record.isTransfer:
                self.app.push_screen(TransferModal(record), callback=check_result)
            else:
                filled_form = self.record_form.get_filled_form(record.id)
                self.app.push_screen(RecordModal("Edit Record", filled_form), callback=check_result)

    def action_delete_record(self) -> None:
        def check_delete(result: bool) -> None:
            if result:
                delete_record(self.current_row)
                self.app.notify(title="Success", message=f"Record deleted", severity="information", timeout=3)
                self.update_account_balance(self.current_row)
                self.build_table()
        
        self.app.push_screen(ConfirmationModal("Are you sure you want to delete this record?"), check_delete)
    
    def action_new_transfer(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_record(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:
                    self.app.notify(title="Success", message=f"Record created", severity="information", timeout=3)
                    self.update_account_balance(result['accountId'])
                    self.update_account_balance(result['transferToAccountId'])
                    self.build_table()
            else:
                self.app.notify(title="Discarded", message=f"Record not updated", severity="warning", timeout=3)
                    
        self.app.push_screen(TransferModal(), callback=check_result)

    # --------------- View --------------- #
    
    def compose(self) -> ComposeResult:
        self.basePage = BasePage(
            pageName="Home",
            bindings=[
                (CONFIG["hotkeys"]["new"], "new_record", "Add", self.action_new_record), 
            ],
        )
        with self.basePage:
            with Horizontal(classes="home-accounts-list"):
                for account in get_all_accounts_with_balance():
                    with Container(classes="account-container"):
                        yield Label(
                            f"[bold]{account.name}[/bold][italic] {account.description or ''}[/italic]",
                            classes="account-name",
                            markup=True
                        )
                        yield Label(
                            f"${account.balance}",
                            classes="account-balance",
                            id=f"account-{account.id}-balance"
                        )
            yield Rule(classes="home-divider", line_style="double")
            yield DataTable(
                id="records-table", 
                cursor_type="row", 
                cursor_foreground_priority=True, 
                zebra_stripes=True
            )
            if not get_accounts_count() or not get_categories_count():
                yield Label(
                    "Please create at least one account and one category to get started.",
                    classes="label-empty"
                )