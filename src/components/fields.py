from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Input, Label, Static

from components.autocomplete import AutoComplete, Dropdown, DropdownItem


class Field(Static):
    def __init__(self, field: dict):
        super().__init__()
        self.field = field
        self.input = Input(placeholder=self.field.get("placeholder", ""),
                            id=f"field-{self.field['key']}",
                        )
        if self.field["type"] == "autocomplete":
            self.input.__setattr__("heldValue", self.field.get("defaultValue", ""))
            self.input.value = str(self.field.get("defaultValue", ""))
    
    def on_auto_complete_selected(self, event: AutoComplete.Selected) -> None:
        for item in self.field["options"]:
            if str(item.get("text", item["value"])) == str(event.item.main):
                ## set a new property on the input widget
                self.input.heldValue = item["value"]
        

    def compose(self) -> ComposeResult:
        if self.field["type"] != "hidden":
            with Container(classes="row", id=f"row-field-{self.field['key']}"):
                yield Label(f"{self.field['title']}:")
                if self.field["type"] == "autocomplete":
                    yield AutoComplete(
                        self.input,
                        Dropdown(items=[
                            DropdownItem(item.get("text", item["value"]),
                                        item.get("prefix", ""),
                                        item.get("postfix", "⇥")) for item in self.field["options"]
                        ])
                    )
                else:
                    yield Input(placeholder=self.field.get("placeholder", ""),
                            id=f"field-{self.field['key']}",
                            value=self.field.get("defaultValue", "")
                        )
        else:
            self.input = Static(id=f"field-{self.field['key']}")
            self.input.__setattr__("heldValue", self.field.get("defaultValue", ""))
            yield self.input
