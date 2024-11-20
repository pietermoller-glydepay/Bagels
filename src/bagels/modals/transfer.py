from datetime import datetime

from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import (
    Label,
    ListItem,
    ListView,
)

from bagels.components.fields import Fields
from bagels.managers.accounts import get_all_accounts_with_balance
from bagels.utils.validation import validateForm
from bagels.modals.base_widget import ModalContainer
from bagels.forms.form import Form, FormField


class Accounts(ListView):
    def __init__(self, accounts, initial_id: int = 0, type: str = "", *args, **kwargs):
        initial_index = accounts.index(
            next((account for account in accounts if account.id == initial_id), None)
        )
        super().__init__(
            *[
                ListItem(
                    Label(
                        str(account.name),
                        classes="name " + ("hidden-name" if account.hidden else ""),
                    ),
                    Label(
                        str(account.balance),
                        classes="balance "
                        + ("hidden-balance" if account.hidden else ""),
                    ),
                    classes="item",
                    id=f"account-{account.id}",
                )
                for account in accounts
            ],
            id=f"{type}-accounts",
            classes="accounts",
            initial_index=initial_index,
            *args,
            **kwargs,
        )


class TransferModal(ModalScreen):
    def __init__(self, record=None, *args, **kwargs):
        super().__init__(classes="modal-screen", *args, **kwargs)
        self.accounts = get_all_accounts_with_balance(get_hidden=True)
        self.form = Form(
            fields=[
                FormField(
                    title="Label",
                    key="label",
                    type="string",
                    placeholder="Label",
                    is_required=True,
                    default_value=str(record.label) if record else "",
                ),
                FormField(
                    title="Amount",
                    key="amount",
                    type="number",
                    placeholder="0.00",
                    min=0,
                    is_required=True,
                    default_value=str(record.amount) if record else "",
                ),
                FormField(
                    title="Date",
                    key="date",
                    type="dateAutoDay",
                    placeholder="dd (mm) (yy)",
                    default_value=(
                        record.date.strftime("%d")
                        if record
                        else datetime.now().strftime("%d")
                    ),
                ),
            ]
        )
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
        # custom check for from and to accounts
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
                    Accounts(self.accounts, initial_id=self.fromAccount, type="from"),
                    Label(">>>", classes="arrow"),
                    Accounts(self.accounts, initial_id=self.toAccount, type="to"),
                    classes="transfer-accounts-container",
                ),
                Label(id="transfer-error"),
                id="transfer-modal",
            ),
            custom_classes="wrapper max-width-80",
        )
