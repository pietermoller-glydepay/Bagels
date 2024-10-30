
from datetime import datetime

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Input, Label, ListItem, ListView

from components.fields import Fields
from controllers.accounts import get_all_accounts_with_balance
from utils.form import validateForm


class ConfirmationModal(ModalScreen):
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(id="confirmation-modal-screen", *args, **kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(classes="dialog"):
            yield Label(self.message)

    def on_key(self, event: events.Key):
        if event.key == "enter":
            self.dismiss(True)
        elif event.key == "escape":
            self.dismiss(False)

class InputModal(ModalScreen):
    def __init__(self, title: str, form: list[dict], *args, **kwargs):
        super().__init__(id="input-modal-screen", *args, **kwargs)
        self.title = title
        self.form = form

    def compose(self) -> ComposeResult:
        with Container(classes="input-dialog"):
            yield Label(f"[bold]{self.title}[/bold]", classes="input-dialog-title")
            yield Fields(self.form)
    
    # --------------- Hooks -------------- #

    def on_key(self, event: events.Key):
        if event.key == "down":
            self.screen.focus_next()
        elif event.key == "up":
            self.screen.focus_previous()
        elif event.key == "enter":
            self.action_submit()
        elif event.key == "escape":
            self.dismiss(None)

    # ------------- Callbacks ------------ #

    def action_submit(self):
        resultForm, errors, isValid = validateForm(self, self.form)
        if isValid:
            self.dismiss(resultForm)
        else: 
            previousErrors = self.query(".error")
            for error in previousErrors:
                error.remove()
            for key, value in errors.items():
                field = self.query_one(f"#row-field-{key}")
                field.mount(Label(value, classes="error"))

class TransferModal(ModalScreen):
    def __init__(self, record=None, *args, **kwargs):
        super().__init__(id="transfer-modal-screen", *args, **kwargs)
        self.accounts = get_all_accounts_with_balance()
        self.form = [
            {
                "title": "Label",
                "key": "label",
                "type": "string",
                "placeholder": "Label",
                "isRequired": True,
                "defaultValue": str(record.label) if record else ""
            },
            {
                "title": "Amount",
                "key": "amount",
                "type": "number",
                "placeholder": "0.00",
                "min": 0,
                "isRequired": True,
                "defaultValue": str(record.amount) if record else ""
            },
            {
                "placeholder": "dd (mm) (yy)",
                "title": "Date",
                "key": "date",
                "type": "dateAutoDay",
                "defaultValue": record.date.strftime("%d") if record else datetime.now().strftime("%d")
            }
        ]
        self.fromAccount = record.accountId if record else self.accounts[0]["id"]
        self.toAccount = record.transferToAccountId if record else self.accounts[1]["id"]
        if record:
            self.label = "Edit transfer"
        else:
            self.label = "New transfer"
        self.atAccountList = False
    
    def on_key(self, event: events.Key):
        if self.atAccountList:
            if event.key == "right":
                self.screen.focus_next()
            elif event.key == "left":
                self.screen.focus_previous()
        else:
            if event.key == "up":
                self.screen.focus_previous()
            elif event.key == "down":
                self.screen.focus_next()
        if event.key == "enter":
            self.action_submit()
        elif event.key == "escape":
            self.dismiss(None)
    
    def on_list_view_highlighted(self, event: ListView.Highlighted):
        accountId = event.item.id.split("-")[1]
        if event.list_view.id == "from-accounts":
            self.fromAccount = accountId
        elif event.list_view.id == "to-accounts":
            self.toAccount = accountId
            
    def action_submit(self):
        resultForm, errors, isValid = validateForm(self, self.form)
        if self.fromAccount == self.toAccount:
            self.query_one("#transfer-error").update("From and to accounts cannot be the same")
        else:
            self.query_one("#transfer-error").update("")
            if isValid:
                resultForm["accountId"] = self.fromAccount
                resultForm["transferToAccountId"] = self.toAccount
                resultForm["isTransfer"] = True
                self.dismiss(resultForm)
            else: 
                previousErrors = self.query(".error")
                for error in previousErrors:
                    error.remove()
                for key, value in errors.items():
                    field = self.query_one(f"#row-field-{key}")
                    field.mount(Label(value, classes="error"))
    
    def compose(self) -> ComposeResult:
        with Container(classes="transfer-modal"):
            yield Label(f"[bold]{self.label}[/bold]", classes="title")
            yield Fields(self.form)
            with Container(id="accounts-container"):
                yield ListView(
                        *[ListItem(
                                Label(f"{account["name"]} (Bal: [yellow]{account['balance']}[/yellow])", classes="account-name"),
                                classes="item",
                                id=f"account-{account['id']}"
                            ) for account in self.accounts]
                        , id="from-accounts", 
                        classes="accounts",
                        initial_index=self.fromAccount - 1
                    )
                yield Label("[italic]-- to ->[/italic]", classes="arrow")
                yield ListView(
                        *[ListItem(
                                Label(f"{account["name"]} (Bal: [yellow]{account['balance']}[/yellow])", classes="account-name"),
                                classes="item",
                                id=f"account-{account['id']}"
                            ) for account in self.accounts]
                        , id="to-accounts",
                        classes="accounts",
                        initial_index=self.toAccount - 1
                    )
            yield Label(id="transfer-error")
