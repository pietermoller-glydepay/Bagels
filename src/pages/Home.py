import copy
from datetime import datetime
from time import sleep

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Label, Static

from components.base import BasePage
from components.datatable import DataTable
from components.indicators import EmptyIndicator
from components.modals import (ConfirmationModal, InputModal, RecordModal,
                               TransferModal)
from config import CONFIG
from controllers.accounts import (get_account_balance_by_id,
                                  get_accounts_count, get_all_accounts,
                                  get_all_accounts_with_balance)
from controllers.categories import (get_all_categories_by_freq,
                                    get_all_categories_tree,
                                    get_categories_count)
from controllers.records import (create_record, create_record_and_splits,
                                 delete_record, get_record_by_id,
                                 get_record_total_split_amount, get_records,
                                 is_record_all_splits_paid, update_record,
                                 update_record_and_splits)
from controllers.splits import create_split
from utils.format import format_date_to_readable
from utils.forms import RecordForm


class Page(Static):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.filter = {
            "month_offset": 0,
            "sort_by": "date",
            "sort_direction": "desc"
        }
        self.record_form = RecordForm()
        self.isReady = get_accounts_count() and get_categories_count()
        self.show_splits = True
    
    def on_mount(self) -> None:
        self._build_table()
        if get_accounts_count() > 1:
            self.basePage.newBinding("ctrl+t", "new_transfer", "Transfer", self.action_new_transfer)
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key:
            self.current_row = event.row_key.value
            
    
    # -------------- Helpers ------------- #

    def _update_month_label(self) -> None:
        def get_month_label() -> Label:
            return self.query_one("#current-month-label")

        label = get_month_label()
        match self.filter["month_offset"]:
            case 0:
                label.update("Current Month")
            case -1:
                label.update("Previous Month")
            case _:
                label.update(f"{datetime(datetime.now().year, datetime.now().month + self.filter['month_offset'], 1).strftime('%B %Y')}")
        
    
    def _build_table(self) -> None:
        table: DataTable = self.query_one("#records-table")
        empty_indicator: Static = self.query_one("#empty-indicator")
        table.clear()
        if not table.columns:
            table.add_columns(" ", "Date", "Category", "Amount", "Label", "Account")
        records = get_records(**self.filter)
        if records: 
            for record in records:
                # Cash flow indicator for amount
                flow_icon_positive = "[green]+[/green]"
                flow_icon_negative = "[red]-[/red]"
                flow_icon = flow_icon_positive if record.isIncome else flow_icon_negative
                # Split indicator at the left of the row
                if record.splits:
                    if is_record_all_splits_paid(record.id):
                        left_icon = "[green]●[/green]"
                    else:
                        left_icon = "[red]●[/red]"
                else:
                    left_icon = " "
                # Category string
                if record.isTransfer:
                    category_string = record.account.name + " → " + record.transferToAccount.name
                    amount_string = record.amount
                else:
                    color_tag = record.category.color.lower()
                    category_string = f"[{color_tag}]●[/{color_tag}] {record.category.name}"
                    amount_string = f"{flow_icon} {record.amount}"
                # Label string
                if record.label:
                    label_string = record.label
                else:
                    label_string = "-"
                # Add row to table
                table.add_row(
                    left_icon,
                    format_date_to_readable(record.date),
                    category_string,
                    amount_string,
                    label_string,
                    record.account.name,
                    key=str(record.id),
                )
                # ----- Handle displaying splits ----- #
                if record.splits and self.show_splits:
                    total_split_count = len(record.splits)
                    amount_self = record.amount - get_record_total_split_amount(record.id)
                    split_flow_icon = flow_icon_negative if record.isIncome else flow_icon_positive
                    for index, split in enumerate(record.splits):
                        if index == total_split_count - 1:
                            left_icon = "└"
                        else:
                            left_icon = "├"
                        if split.isPaid:
                            paid_status = f"[green]●[/green] {format_date_to_readable(split.paidDate)}"
                            left_icon = f"[green]{left_icon}[/green]"
                        else:
                            paid_status = "[red]●[/red] Unpaid"
                            left_icon = f"[red]{left_icon}[/red]"
                        table.add_row(
                            left_icon, # icon row
                            paid_status, # date row
                            f"✦ {split.person.name}", # category row
                            f"{split_flow_icon} {split.amount}", # amount row
                            "-", # label row
                            split.account.name if split.account else "-" # account row
                        )
                    table.add_row(
                        "", # icon row
                        "", # date row
                        "", # category row
                        f"= {amount_self}", # amount row
                        "", # label row
                        "", # account row
                        style_name="net"
                    )
            table.focus()
        else:
            self.current_row = None
        empty_indicator.display = not records
        self._update_month_label()
        
    def _update_account_balance(self) -> None:
        for account in get_all_accounts_with_balance():
            self.query_one(f"#account-{account.id}-balance").update(f"${account.balance}")
    
    def _notify_not_ready(self) -> None:
        self.app.notify(title="Error", message="Please create at least one account and one category to get started.", severity="error", timeout=2)
    
    # ------------- Callbacks ------------ #
        
    def action_toggle_splits(self) -> None:
        self.show_splits = not self.show_splits
        self._build_table()
    
    def action_prev_month(self) -> None:
        self.filter["month_offset"] -= 1
        self._build_table()
    
    def action_next_month(self) -> None:
        if self.filter["month_offset"] < 0:
            self.filter["month_offset"] += 1
            self._build_table()
        else:
            self.app.notify(title="Error", message="You are already on the current month.", severity="error", timeout=2)
            self.app.bell()
    
    def action_new_record(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_record_and_splits(result['record'], result['splits'])
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:   
                    self.app.notify(title="Success", message=f"Record created", severity="information", timeout=3)
                    self._update_account_balance()
                    self._build_table()
        
        if self.isReady:
            self.app.push_screen(RecordModal("New Record", form=self.record_form.get_form()), callback=check_result)
        else:
            self._notify_not_ready()
    
    def action_edit_record(self) -> None:
        if not self.isReady:
            self._notify_not_ready()
            return 
        record = get_record_by_id(self.current_row)
        def check_result(result: bool) -> None:
            if result:
                try:
                    update_record_and_splits(self.current_row, result['record'], result['splits'])
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:
                    self.app.notify(title="Success", message=f"Record updated", severity="information", timeout=3)
                    self._update_account_balance()
                    if record.isTransfer:
                        self._update_account_balance()
                    self._build_table()
            else:
                self.app.notify(title="Discarded", message=f"Record not updated", severity="warning", timeout=3)
        
        if record:
            if record.isTransfer:
                self.app.push_screen(TransferModal(record), callback=check_result)
            else:
                filled_form, filled_splits = self.record_form.get_filled_form(record.id)
                self.app.push_screen(RecordModal("Edit Record", form=filled_form, splitForm=filled_splits, isEditing=True), callback=check_result)
        else:
            # might be a split
            if False:
                pass
            else: # utility row
                self.app.notify(title="Utility row", message="Nothing to edit.", severity="warning", timeout=2)

    def action_delete_record(self) -> None:
        def check_delete(result: bool) -> None:
            if result:
                delete_record(self.current_row)
                self.app.notify(title="Success", message=f"Record deleted", severity="information", timeout=3)
                self._update_account_balance()
                self._build_table()
        if not self.isReady:
            self._notify_not_ready()
            return
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
                    self._update_account_balance()
                    self._update_account_balance()
                    self._build_table()
            else:
                self.app.notify(title="Discarded", message=f"Record not updated", severity="warning", timeout=3)
        if get_accounts_count() > 1:
            self.app.push_screen(TransferModal(), callback=check_result)
        else:
            self.app.notify(title="Error", message="Please have at least two accounts to create a transfer.", severity="error", timeout=2)

    # --------------- View --------------- #
    
    def compose(self) -> ComposeResult:
        self.basePage = BasePage(
            pageName="Home",
            bindings=[
                (CONFIG.hotkeys.new, "new_record", "Add", self.action_new_record),
                (CONFIG.hotkeys.delete, "delete_record", "Delete", self.action_delete_record),
                (CONFIG.hotkeys.edit, "edit_record", "Edit", self.action_edit_record),
                (CONFIG.hotkeys.home.new_transfer, "new_transfer", "Transfer", self.action_new_transfer),
                (CONFIG.hotkeys.home.toggle_splits, "toggle_splits", "Toggle Splits", self.action_toggle_splits),
                ("left", "prev_month", "Previous Month", self.action_prev_month),
                ("right", "next_month", "Next Month", self.action_next_month),
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
            with Container(classes="month-selector"):
                yield Label("Current Month", id="current-month-label")
                yield Label("<<<", classes="arrow-left")
                yield Label(">>>", classes="arrow-right")
            yield DataTable(
                id="records-table", 
                cursor_type="row", 
                cursor_foreground_priority=True, 
                zebra_stripes=True,
                additional_classes=["datatable--net-row"]   
            )
            yield EmptyIndicator("No entries")
            if not self.isReady:
                yield Label(
                    "Please create at least one account and one category to get started.",
                    classes="label-empty"
                )