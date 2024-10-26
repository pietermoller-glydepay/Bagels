from datetime import datetime
from textual.app import ComposeResult
from textual.widgets import Label
from textual.screen import ModalScreen
from textual.containers import Container
from textual import events
from components.fields import Field
from utils.form import validateForm

NEW_RECORD_FORM = [
    {
        "placeholder": "Label",
        "title": "Label",
        "key": "label",
        "type": "string",
    },
    {
        "placeholder": "0.00",
        "title": "Amount",
        "key": "amount",
        "type": "number",
    },
    {
        "placeholder": "dd (mm) (yy)",
        "title": "Date",
        "key": "date",
        "type": "dateAutoDay",
        "defaultValue": datetime.now().strftime("%d")
    },
]


class NewRecordModal(ModalScreen):
    
    def __init__(self, *args, **kwargs):
        super().__init__(id="input-modal-screen", *args, **kwargs)

    def compose(self) -> ComposeResult:
        with Container(classes="input-dialog"):
            yield Label("New record")
            for field in NEW_RECORD_FORM:
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
        resultForm, errors, isValid = validateForm(self, NEW_RECORD_FORM)
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