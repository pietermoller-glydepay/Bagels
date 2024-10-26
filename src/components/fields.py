from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Input, Static

class Field(Static):
    def __init__(self, placeholder: str, title: str, name: str, type: str, defaultValue: str):
        super().__init__()
        self.placeholder = placeholder
        self.title = title
        self._name = name
        self.type = type
        self.defaultValue = defaultValue
        
    @property
    def name(self):
        return self._name

    def compose(self) -> ComposeResult:
        with Container(classes="row"):
            yield Label(f"{self.title}:")
            yield Input(placeholder=self.placeholder, id=self.name, value=self.defaultValue)
