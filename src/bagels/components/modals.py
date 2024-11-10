from datetime import datetime
from re import M

from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import (Footer, Header, Input, Label, ListItem, ListView,
                             Rule, Static)

from bagels.components.autocomplete import AutoComplete, Dropdown, DropdownItem
from bagels.components.fields import Fields
from bagels.config import CONFIG
from bagels.models.person import Person
from bagels.models.split import Split
from bagels.queries.accounts import get_all_accounts_with_balance
from bagels.queries.persons import create_person, get_all_persons
from bagels.utils.record_forms import RecordForm
from bagels.utils.validation import validateForm


#region Confirma
class ConfirmationModal(ModalScreen):
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(id="confirmation-modal-screen", *args, **kwargs)
        self.message = message

    def compose(self) -> ComposeResult:
        dialog = Container(classes="dialog")
        dialog.border_title = "Alert"
        with dialog:
            yield Label(self.message)

    def on_key(self, event: events.Key):
        if event.key == "enter":
            self.dismiss(True)
        elif event.key == "escape":
            self.dismiss(False)

#region Container
class ModalContainer(Widget):
    # usage: ModalContainer(w1, w2, w3..... hotkeys=[])
    def __init__(self, *content, custom_classes: str = "wrapper max-width-60"):
        super().__init__(classes=custom_classes)
        self.content = content
        # self.hotkeys = hotkeys

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Container(classes="container"):
            for widget in self.content:
                yield widget
        yield Footer(show_command_palette=False)

#region Base
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

#region Transfer

class Accounts(ListView):
    def __init__(self, accounts, initial_index: int = 0, type: str = "", *args, **kwargs):
        super().__init__(
            *[ListItem(
                    Label(str(account.name), classes="name " + ("hidden-name" if account.hidden else "")), 
                    Label(str(account.balance), classes="balance " + ("hidden-balance" if account.hidden else "")), 
                    classes="item", 
                    id=f"account-{account.id}"
                ) for account in accounts],
            id=f"{type}-accounts", 
            classes="accounts", 
            initial_index=initial_index, 
            *args, 
            **kwargs
        )
    
class TransferModal(ModalScreen):
    def __init__(self, record=None, *args, **kwargs):
        super().__init__(classes="modal-screen", *args, **kwargs)
        self.accounts = get_all_accounts_with_balance(get_hidden=True)
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
        self.fromAccount = record.accountId if record else self.accounts[0].id
        self.toAccount = record.transferToAccountId if record else self.accounts[1].id
        if record:
            self.title = "Edit transfer"
        else:
            self.title = "New transfer"
        self.atAccountList = False
    
    def on_descendant_focus(self, event: events.DescendantFocus):
        id = event.widget.id
        if id.endswith("-accounts"):
            self.atAccountList = True
        else:
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
        transfer_error_label = self.query_one("#transfer-error")
        if self.fromAccount == self.toAccount:
            transfer_error_label.update("From and to accounts cannot be the same")
            transfer_error_label.add_class("active")
        else:
            transfer_error_label.update("")
            transfer_error_label.remove_class("active")
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
                    Accounts(
                        self.accounts, 
                        initial_index=self.fromAccount - 1, 
                        type="from"
                    ),
                    Label(">>>", classes="arrow"),
                    Accounts(
                        self.accounts, 
                        initial_index=self.toAccount - 1, 
                        type="to"
                    ),
                    classes="transfer-accounts-container"
                ),
                Label(id="transfer-error"),
                id="transfer-modal"
            ),
            custom_classes="wrapper max-width-80"
        )

#region Record
class RecordModal(InputModal):
    
    isEditing = False
    
    BINDINGS = [
        Binding(CONFIG.hotkeys.record_modal.new_split, "add_split", "Add split", priority=True),
        Binding(CONFIG.hotkeys.record_modal.new_paid_split, "add_paid_split", "Add paid split", priority=True),
        Binding(CONFIG.hotkeys.record_modal.delete_last_split, "delete_last_split", "Delete last split", priority=True)
    ] 
    
    def __init__(self, title: str, form: list[dict] = [], splitForm: list[dict] = [], isEditing: bool = False, *args, **kwargs):
        super().__init__(title, form, *args, **kwargs)
        self.record_form = RecordForm()
        self.splitForm = splitForm
        self.isEditing = isEditing
        if isEditing: 
            self._bindings.key_to_bindings.clear()
            self.refresh_bindings()
        self.splitFormOneLength = len(self.record_form.get_split_form(0, False))
        self.splitCount = int(len(splitForm) / self.splitFormOneLength)
        self.persons = get_all_persons()
        self.accounts = get_all_accounts_with_balance()
        self.total_amount = 0
        self.split_total = Label("", id="split-total")
    
    def on_mount(self):
        self._update_split_total()
        if self.splitCount > 0:
            self._update_split_total_visibility(True)
    
    # -------------- Helpers ------------- #
    
    def _get_splits_from_result(self, resultForm: dict):
        splits = []
        for i in range(0, self.splitCount):
            splits.append({
                "personId": resultForm[f"personId-{i}"],
                "amount": resultForm[f"amount-{i}"],
                "isPaid": resultForm[f"isPaid-{i}"],
                "accountId": resultForm[f"accountId-{i}"],
                "paidDate": resultForm[f"paidDate-{i}"]
            })
        return splits

    def _update_split_total(self, update_new: bool = True):
        my_amount = self.query_one("#field-amount").value
        total = float(my_amount) if my_amount else 0
        if update_new:
            for i in range(0, self.splitCount):
                amount = self.query_one(f"#field-amount-{i}").value
                total += float(amount) if amount else 0
        self.total_amount = total
        if self.splitCount > 0:
            self.split_total.update(f"Total amount: [bold yellow]{total:.2f}[/bold yellow]")
    
    def _get_split_widget(self, index: int, fields: list[dict], isPaid: bool):
        widget = Container(
                Fields(fields),
                id=f"split-{index}",
                classes="split"
            )
        widget.border_title = "> Paid split <" if isPaid else "> Split <"
        return widget
    def _get_init_split_widgets(self):
        widgets = []
        for i in range(0, self.splitCount):
            oneSplitForm = self.splitForm[i * self.splitFormOneLength: (i + 1) * self.splitFormOneLength]
            # Find the isPaid field in the form fields for this split
            isPaid = False
            for field in oneSplitForm:
                if field.get("id") == f"isPaid-{i}":
                    isPaid = field.get("value", False)
                    break
            widgets.append(self._get_split_widget(i, oneSplitForm, isPaid))
        return widgets
    
    def _update_split_total_visibility(self, mount: bool):
        if mount:
            self.query_one(".container").mount(self.split_total)
        else:
            self.split_total.remove()
        
    def _update_errors(self, errors: dict):
        previousErrors = self.query(".error")
        for error in previousErrors:
            error.remove()
        for key, value in errors.items():
            field = self.query_one(f"#row-field-{key}")
            field.mount(Label(value, classes="error"))
        
    def on_auto_complete_created(self, event: AutoComplete.Created) -> None:
        name = event.item.create_option_text
        person = create_person({"name": name})
        for field in self.splitForm:
            if field["key"].startswith("personId"):
                field["options"].append({"text": person.name, "value": person.id})
        for i in range(0, self.splitCount):
            dropdown: Dropdown = self.query_one(f"#dropdown-personId-{i}")
            dropdown.items.append(DropdownItem(person.name, "", ""))
    
    # def on_auto
    
    # ------------- Callbacks ------------ #
    
    def on_input_changed(self, event: Input.Changed):
        if event.input.id.startswith("field-amount"):
            self._update_split_total()
    
    def on_key(self, event: events.Key):
        match event.key:
            case "down":
                self.screen.focus_next()
            case "up":
                self.screen.focus_previous()
            case "enter":
                self.action_submit()
            case "escape":
                self.dismiss(None)
            case _:
                pass
    
    def action_add_paid_split(self):
        self.action_add_split(paid=True)
    
    def action_add_split(self, paid: bool = False):
        splits_container = self.query_one("#splits-container", Container)
        current_split_index = self.splitCount
        new_split_form_fields = self.record_form.get_split_form(current_split_index, paid)
        for field in new_split_form_fields:
            self.splitForm.append(field)
        splits_container.mount(
            self._get_split_widget(current_split_index, new_split_form_fields, paid)
        )
        # Use call_after_refresh to ensure the mount is complete
        splits_container.call_after_refresh(lambda: self.query_one(f"#field-personId-{current_split_index}").focus())
        self.splitCount += 1
        if self.splitCount == 1:
            self._update_split_total_visibility(True)
            self._update_split_total(update_new=False)

    def action_delete_last_split(self):
        if self.splitCount > 0:
            self.query_one(f"#split-{self.splitCount - 1}").remove()
            self.query_one(f"#dropdown-personId-{self.splitCount - 1}").remove() # idk why this is needed
            for i in range(self.splitFormOneLength):
                self.splitForm.pop()
            self.splitCount -= 1
            if self.splitCount == 0:
                self._update_split_total_visibility(False)

    def action_submit(self):
        # We set the amount field to the total amount for the form to read the value
        input: Input = self.query_one("#field-amount")
        input.__setattr__("heldValue", str(self.total_amount))
        
        resultRecordForm, errors, isValid = validateForm(self, self.form)
        resultSplitForm, errorsSplit, isValidSplit = validateForm(self, self.splitForm)
        if isValid and isValidSplit:
            resultSplits = self._get_splits_from_result(resultSplitForm)
            self.dismiss({
                "record": resultRecordForm,
                "splits": resultSplits
            })
            return 
        self._update_errors({**errors, **errorsSplit})
        # Remove the custom value we set for the field if not valid
        input.__setattr__("heldValue", None)

    # -------------- Compose ------------- #

    def compose(self) -> ComposeResult:
        yield ModalContainer(
            Fields(self.form),
            Container(
                *self._get_init_split_widgets(),
                id="splits-container"
            ),
        )
