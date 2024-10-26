from textual import events
from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Label

from components.fields import Field
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
    def __init__(self, form: list[dict], *args, **kwargs):
        super().__init__(id="input-modal-screen", *args, **kwargs)
        self.form = form

    def compose(self) -> ComposeResult:
        with Container(classes="input-dialog"):
            yield Label("[bold]New Account[/bold]")
            for field in self.form:
                yield Field(field)
    
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
            # transaction = create_transaction(resultForm)
            self.dismiss(resultForm)
        else: 
            previousErrors = self.query(".error")
            for error in previousErrors:
                error.remove()
            for key, value in errors.items():
                field = self.query_one(f"#row-field-{key}")
                field.mount(Label(f"{value}!", classes="error"))