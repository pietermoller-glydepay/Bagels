from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input, Label, Static


class Field(Static):
    def __init__(self, field: dict):
        super().__init__()
        self.field = field

    def compose(self) -> ComposeResult:
        with Container(classes="row", id=f"row-field-{self.field['key']}"):
            yield Label(f"{self.field['title']}:")
            yield Input(placeholder=self.field["placeholder"],
                        id=f"field-{self.field['key']}",
                        value=self.field.get("defaultValue", "")
                    )
