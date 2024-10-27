import copy
from datetime import datetime

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.reactive import reactive
from textual.widgets import Checkbox, DataTable, Label, Rule, Static

from components.base import BasePage
from components.modals import ConfirmationModal, InputModal, TransferModal
from controllers.accounts import (check_any_account, get_account_balance_by_id,
                                  get_all_accounts,
                                  get_all_accounts_with_balance)
from controllers.categories import check_any_category, get_all_categories
from controllers.records import (create_record, delete_record,
                                 get_record_by_id, get_records, update_record)


class Page(Static):
    
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def on_mount(self) -> None:
        self.build_table()
        self.update_record_form()
    
    def on_unmount(self) -> None:
        self.basePage.removeBinding("backspace")
        self.basePage.removeBinding("space")
    
    def update_record_form(self) -> None:
        accounts = get_all_accounts()   
        categories = get_all_categories()
        RECORD_FORM[3]["options"] = [
            {
                "text": account.name,
                "value": account.id
            }
            for account in accounts
        ]
        RECORD_FORM[3]["defaultValue"] = accounts[0].id if accounts else None
        RECORD_FORM[3]["defaultValueText"] = accounts[0].name if accounts else ""
        RECORD_FORM[1]["options"] = [
            {
                "text": category.name,
                "value": category.id
            }
            for category, _ in categories
        ]
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key:
            self.current_row = event.row_key.value

    # ------------- Callbacks ------------ #
    
    def build_table(self) -> None:
        table = self.query_one("#records-table")
        table.clear()
        if not table.columns:
            table.add_columns(" ", "Date", "Category", "Amount", "Label")
        records = get_records()
        if records: 
            self.basePage.newBinding("backspace", "delete_record", "Delete Record", self.action_delete_record)
            self.basePage.newBinding("space", "edit_record", "Edit Record", self.action_edit_record)
            for record in records:
                flow_icon = "[green]+[/green]" if record.isIncome else "[red]-[/red]"
                type_icon = "⏲" if record.isAllUnpaidCleared == False else " "
                if record.isTransfer:
                    category_string = "⇌ Transfer"
                    amount_string = record.amount
                else:
                    color_tag = record.category.color.lower()
                    category_string = f"[{color_tag}]●[/{color_tag}] {record.category.name}"
                    amount_string = f"{flow_icon} {record.amount}"
                table.add_row(type_icon,
                            record.date.strftime("%d-%m"),
                            category_string,
                            amount_string,
                            record.label,
                            key=str(record.id))
        table.zebra_stripes = True
        table.focus()
        
    def update_account_balance(self, account_id: int) -> None:
        self.query_one(f"#account-{account_id}-balance").update(f"${get_account_balance_by_id(account_id)}")
    
    def action_new_record(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try: 
                    create_record(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:   
                    self.app.notify(title="Success", message=f"Record created", severity="information", timeout=3)
                    self.update_account_balance(result['accountId'])
                    self.build_table()
        
        self.app.push_screen(InputModal("New Record", RECORD_FORM), callback=check_result)
    
    def action_edit_record(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    update_record(self.current_row, result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:
                    self.app.notify(title="Success", message=f"Record updated", severity="information", timeout=3)
                    self.update_account_balance(result['accountId'])
                    self.build_table()
            else:
                self.app.notify(title="Discarded", message=f"Record not updated", severity="warning", timeout=3)
        
        record = get_record_by_id(self.current_row)
        if record:
            filled_record_form = copy.deepcopy(RECORD_FORM)
            for field in filled_record_form:
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
            self.app.push_screen(InputModal("Edit Record", filled_record_form), callback=check_result)

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
                ("ctrl+t", "new_transfer", "Transfer", self.action_new_transfer),
            ],
        )
        with self.basePage:
            with Horizontal(classes="home-accounts-list"):
                for account in get_all_accounts_with_balance():
                    with Container(classes="account-container"):
                        yield Label(f"[bold]{account['name']}[/bold][italic] {account['description'] or ""}[/italic]", classes="account-name", markup=True)
                        yield Label(f"${account['balance']}", classes="account-balance", id=f"account-{account['id']}-balance")
            yield Rule(classes="home-divider", line_style="double")
            yield DataTable(id="records-table", cursor_type="row")
            if not check_any_account() and not check_any_category():
                yield Label("Please create at least one account and one category to get started.", classes="label-empty")

RECORD_FORM = [
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