from datetime import datetime

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import (Footer, Header, Input, Label, ListItem, ListView,
                             Rule)

from components.fields import Fields
from controllers.accounts import get_all_accounts_with_balance
from controllers.persons import create_person, get_all_persons
from models.split import Split
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

class ModalContainer(Widget):
    # usage: ModalContainer(w1, w2, w3..... hotkeys=[])
    def __init__(self, *content, hotkeys: list[dict] = []):
        super().__init__(classes="wrapper")
        self.content = content
        self.hotkeys = hotkeys

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(classes="container"):
            for widget in self.content:
                yield widget
        with Container(classes="footer"):
            for hotkey in self.hotkeys:
                yield Label(f"[bold yellow]{hotkey['key']}[/bold yellow] {hotkey['label']}")

class InputModal(ModalScreen):
    def __init__(self, title: str, form: list[dict], *args, **kwargs):
        super().__init__(classes="modal-screen", *args, **kwargs)
        self.title = title
        self.form = form
    
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

    # -------------- Compose ------------- #
    
    def compose(self) -> ComposeResult:
        yield ModalContainer(Fields(self.form))

class TransferModal(ModalScreen):
    def __init__(self, record=None, *args, **kwargs):
        super().__init__(classes="modal-screen", *args, **kwargs)
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
            self.title = "Edit transfer"
        else:
            self.title = "New transfer"
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
        yield ModalContainer(
            Container(
                Fields(self.form),
                Container(
                    ListView(
                            *[ListItem(
                                Label(f"{account["name"]} (Bal: [yellow]{account['balance']}[/yellow])", classes="account-name"),
                                    classes="item",
                                    id=f"account-{account['id']}"
                                ) for account in self.accounts]
                            , id="from-accounts", 
                            classes="accounts",
                            initial_index=self.fromAccount - 1
                        ),
                    Label("[italic]-- to ->[/italic]", classes="arrow"),
                    ListView(
                        *[ListItem(
                                Label(f"{account["name"]} (Bal: [yellow]{account['balance']}[/yellow])", classes="account-name"),
                                classes="item",
                                id=f"account-{account['id']}"
                            ) for account in self.accounts]
                            , id="to-accounts",
                            classes="accounts",
                        initial_index=self.toAccount - 1
                    ),
                    id="accounts-container"
                ),
                Label(id="transfer-error"),
                id="transfer-modal"
            )
        )

class RecordModal(InputModal):
    def __init__(self, title: str, *args, **kwargs):
        super().__init__(title, *args, **kwargs)
        self.splits = []
        self.persons = get_all_persons()
        self.split_form = [
            {
                "title": "Person",
                "key": "person_id", 
                "type": "autocomplete",
                "options": [{"text": person.name, "value": person.id} for person in self.persons],
                "create_action": self.action_create_person,
                "isRequired": True,
                "placeholder": "Select Person"
            },
            {
                "title": "Amount",
                "key": "amount",
                "type": "number", 
                "min": 0,
                "isRequired": True,
                "placeholder": "0.00"
            }
        ]

    def on_key(self, event: events.Key):
        if event.key == "down":
            self.screen.focus_next()
        elif event.key == "up":
            self.screen.focus_previous()
        elif event.key == "enter":
            self.action_submit()
        elif event.key == "escape":
            self.dismiss(None)
        elif event.key == "ctrl+a":
            self.action_add_split()
        elif event.key == "ctrl+d":
            self.action_delete_last_split()
    
    def action_create_person(self, name: str):
        create_person({"name": name})

    def action_add_split(self):
        splits_container = self.query_one("#splits-container", Container)
        self.splits.append(self.split_form)
        splits_container.mount(
            Container(
                Fields(self.split_form),
                id=f"split-{len(self.splits)}",
                classes="split"
            )
        )

    def action_delete_last_split(self):
        if len(self.splits) > 0:
            self.query_one(f"#split-{len(self.splits)}").remove()
            self.splits.pop()

    def action_submit(self):
        resultForm, errors, isValid = validateForm(self, self.form)
        if isValid:
            # Validate and collect splits data
            splits_valid = True
            self.splits = []
            
            for split_id in range(len(self.query("#splits-container Fields"))):
                split_result, split_errors, split_valid = validateForm(
                    self,
                    self.split_form,
                    form_id=f"split-{split_id}"
                )
                if split_valid:
                    # Add person name for display purposes
                    person = next(p for p in self.persons if p.id == split_result["person_id"])
                    split_result["person_name"] = person.name
                    self.splits.append(split_result)
                else:
                    splits_valid = False
                    # Show errors on split forms
                    split_container = self.query_one(f"#split-{split_id}")
                    for key, value in split_errors.items():
                        field = split_container.query_one(f"#row-field-{key}")
                        field.mount(Label(value, classes="error"))

            if splits_valid:
                if self.splits:
                    resultForm["splits"] = self.splits
                self.dismiss(resultForm)
        else:
            previousErrors = self.query(".error")
            for error in previousErrors:
                error.remove()
            for key, value in errors.items():
                field = self.query_one(f"#row-field-{key}")
                field.mount(Label(value, classes="error"))

    def compose(self) -> ComposeResult:
        yield ModalContainer(
            Fields(self.form),
            Container(id="splits-container"),
            hotkeys=[
                {"key": "^a", "label": "Split amount"},
                {"key": "^d", "label": "Delete split"}
            ]
        )
