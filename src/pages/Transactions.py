from itertools import cycle
from typing import Callable
from textual.binding import Binding
from textual.app import ComposeResult
from textual.containers import Horizontal, Container
from textual.screen import ModalScreen
from textual.widgets import Label, Input, Button, Switch, Static, Footer, DataTable
from textual import events
from components.fields import Field
from models.Transaction import FORM
from controllers.transactions import create_transaction, get_transactions
from components.base import BasePage
from utils.form import validateForm

class NewTransactionModal(ModalScreen):

    def compose(self) -> ComposeResult:
        with Container(classes="dialog"):
            for field in FORM:
                yield Field(
                    placeholder=field["placeholder"],
                    title=field["title"],
                    name=field["title"].lower(),
                    type=field["type"],
                    defaultValue=field.get("defaultValue", "")
                )
            yield Button("Submit", id="submit-btn")

    def on_key(self, event: events.Key):
        if event.key == "down":
            self.screen.focus_next()
        elif event.key == "up":
            self.screen.focus_previous()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit-btn":
            self.action_submit()

    def action_submit(self):
        resultForm, errors, isValid = validateForm(self, FORM)
        if isValid:
            transaction = create_transaction(resultForm)
            self.dismiss(True)
        else: 
            error_string = "\n".join([f"{key}: {value}" for key, value in errors.items()])
            self.mount(Label(error_string))


class Page(Static):
    def on_mount(self) -> None:
        self.build_table()

    def build_table(self) -> None:
        table = self.query_one("#transactions-table")
        table.clear()
        if not table.columns:
            table.add_columns(*[field["title"] for field in FORM])
        table.add_rows(get_transactions())
        table.cursor_type = 'cell'
        table.zebra_stripes = True
        table.focus()

    # ------------- Callbacks ------------ #

    def action_new_transaction(self) -> None:
        def checkQuit(result: bool) -> None:
            if result:
                self.build_table()
        
        self.app.push_screen(NewTransactionModal(), checkQuit)

    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        with BasePage(
            pageName="Transactions",
            bindings=[("ctrl+n", "new_transaction", "New Transaction", self.action_new_transaction)],
        ):
            yield DataTable(id="transactions-table")
