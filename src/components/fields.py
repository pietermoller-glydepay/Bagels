from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Checkbox, Input, Label, Static, Switch

from components.autocomplete import AutoComplete, Dropdown, DropdownItem


class Fields(Static):
    def __init__(self, fields: list[dict]):
        super().__init__()
        self.fields = fields
    
    def compose(self) -> ComposeResult:
        for field in self.fields:
            yield Field(field)

class Field(Static):
    def __init__(self, field: dict):
        super().__init__()
        self.field = field
        self.input = Input(placeholder=self.field.get("placeholder", ""),
                            id=f"field-{self.field['key']}",
                        )
        self.field_type = self.field["type"]
        if self.field_type in ["integer", "number"]:
            self.input.type = self.field_type
        elif self.field_type == "autocomplete":
            self.input.__setattr__("heldValue", self.field.get("defaultValue", ""))
            self.input.value = str(self.field.get("defaultValueText", self.field.get("defaultValue", "")))
        
        if self.field_type not in ["boolean", "autocomplete"]:
            self.input.value = self.field.get("defaultValue", "")
    
    def on_auto_complete_selected(self, event: AutoComplete.Selected) -> None:
        self.screen.focus_next()
        for item in self.field["options"]:
            if str(item.get("text", item["value"])) == str(event.item.main):
                ## set a new property on the input widget
                self.input.heldValue = item["value"]
        

    def compose(self) -> ComposeResult:
        if self.field["type"] != "hidden":
            with Container(classes="row", id=f"row-field-{self.field['key']}"):
                yield Label(f"{self.field['title']}", classes="row-label")
                if self.field["type"] == "autocomplete":
                    yield AutoComplete(
                        self.input,
                        Dropdown(items=[
                            DropdownItem(item.get("text", item["value"]),
                                        item.get("prefix", item["prefix"] if "prefix" in item else ""),
                                        item.get("postfix", item["postfix"] if "postfix" in item else "")) for item in self.field["options"]
                        ], 
                        show_on_focus=True,
                        create_option=True
                        ),
                        classes="field-autocomplete",
                        create_action=self.field.get("create_action", None)
                    )
                elif self.field["type"] == "boolean":
                    with Container(classes="switch-group"):
                        yield Label(f"[italic]{self.field["labels"][0]}[/italic]")
                        yield Switch(id=f"field-{self.field['key']}",
                                    value=self.field.get("defaultValue", False))
                        yield Label(f"[italic]{self.field["labels"][1]}[/italic]")
                else:
                    yield self.input
        else:
            self.input = Static(id=f"field-{self.field['key']}")
            self.input.__setattr__("heldValue", self.field.get("defaultValue", ""))
            yield self.input
