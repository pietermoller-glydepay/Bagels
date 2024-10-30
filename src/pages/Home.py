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


class Page(Static):
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def on_mount(self) -> None:
        self.record_form = RecordForm()
        self.build_table()
        if get_accounts_count() > 1:
            self.basePage.newBinding("ctrl+t", "new_transfer", "Transfer", self.action_new_transfer)
    
    def on_unmount(self) -> None:
        self.basePage.removeBinding("backspace")
        self.basePage.removeBinding("space")
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
            self.basePage.newBinding("backspace", "delete_record", "Delete Record", self.action_delete_record)
            self.basePage.newBinding("space", "edit_record", "Edit Record", self.action_edit_record)
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
                    # Handle splits if present
                    splits = result.pop('splits', [])
                    record = create_record(result)
                    
                    # Create splits if any
                    if splits:
                        for split in splits:
                            split_data = {
                                'recordId': record.id,
                                'personId': split['person_id'],
                                'amount': split['amount'],
                                'isPaid': False
                            }
                            db.session.add(Split(**split_data))
                        db.session.commit()
                        
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
                    # Handle splits if present
                    splits = result.pop('splits', [])
                    update_record(self.current_row, result)
                    
                    # Update splits if any
                    if splits:
                        # Delete existing splits
                        delete_splits_by_record_id(self.current_row)
                        
                        # Create new splits
                        for split in splits:
                            split_data = {
                                'recordId': self.current_row,
                                'personId': split['person_id'],
                                'amount': split['amount'],
                                'isPaid': False
                            }
                            create_split(split_data)
                        
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
                filled_form = self.record_form.get_filled_form(record)
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
                ("ctrl+n", "new_record", "New", self.action_new_record), 
            ],
        )
        with self.basePage:
            with Horizontal(classes="home-accounts-list"):
                for account in get_all_accounts_with_balance():
                    with Container(classes="account-container"):
                        yield Label(
                            f"[bold]{account['name']}[/bold][italic] {account['description'] or ''}[/italic]",
                            classes="account-name",
                            markup=True
                        )
                        yield Label(
                            f"${account['balance']}",
                            classes="account-balance",
                            id=f"account-{account['id']}-balance"
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


class RecordForm:
    def __init__(self):
        self.form = [
            {
                "placeholder": "Label",
                "title": "Label", 
                "key": "label",
                "type": "string",
            },
            {
                "title": "Category",
                "key": "categoryId",
                "type": "autocomplete",
                "options": [],
                "isRequired": True,
                "placeholder": "Select Category"
            },
            {
                "placeholder": "0.00",
                "title": "Amount",
                "key": "amount",
                "type": "number",
                "min": 0,
                "isRequired": True,
            },
            {
                "title": "Account",
                "key": "accountId", 
                "type": "autocomplete",
                "options": [],
                "isRequired": True,
                "placeholder": "Select Account"
            },
            {
                "title": "Type",
                "key": "isIncome",
                "type": "boolean",
                "labels": ["Expense", "Income"],
                "defaultValue": False,
            },
            {
                "placeholder": "dd (mm) (yy)",
                "title": "Date",
                "key": "date",
                "type": "dateAutoDay",
                "defaultValue": datetime.now().strftime("%d")
            }
        ]
        self._populate_form_options()

    def _populate_form_options(self):
        accounts = get_all_accounts_with_balance()   
        self.form[3]["options"] = [
            {
                "text": account["name"],
                "value": account["id"],
                "postfix": Text(f"{account['balance']}", style="yellow")
            }
            for account in accounts
        ]
        if accounts:
            self.form[3]["defaultValue"] = accounts[0]["id"]
            self.form[3]["defaultValueText"] = accounts[0]["name"]

        categories = get_all_categories_by_freq()
        self.form[1]["options"] = [
            {
                "text": category.name,
                "value": category.id,
                "prefix": Text("●", style=category.color),
                "postfix": Text(f"↪ {category.parentCategory.name}" if category.parentCategory else "", style=category.parentCategory.color) if category.parentCategory else ""
            }
            for category, _ in categories
        ]

    def get_filled_form(self, record):
        """Return a copy of the form with values from the record"""
        filled_form = copy.deepcopy(self.form)
        for field in filled_form:
            value = getattr(record, field["key"])
            if field["key"] == "date":
                field["defaultValue"] = value.strftime("%d")
            elif field["key"] == "isIncome":
                field["defaultValue"] = value
            elif field["key"] == "categoryId":
                field["defaultValue"] = record.category.id
                field["defaultValueText"] = record.category.name
            elif field["key"] == "accountId":
                field["defaultValue"] = record.account.id
                field["defaultValueText"] = record.account.name
            else:
                field["defaultValue"] = str(value) if value is not None else ""
        return filled_form

    def get_form(self):
        """Return the base form"""
        return self.form
