from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Checkbox, Input, Label, Static, Switch

from components.autocomplete import AutoComplete, Dropdown, DropdownItem


class Fields(Static):
    """Container for multiple form fields"""
    def __init__(self, fields: list[dict]):
        super().__init__()
        self.fields = fields
    
    def compose(self) -> ComposeResult:
        for field in self.fields:
            yield Field(field)


class Field(Static):
    """Individual form field that can be text, number, boolean, or autocomplete"""
    def __init__(self, field: dict):
        super().__init__()
        self.field = field
        self.field_type = field["type"]
        
        # Create base input widget
        self.input = Input(
            placeholder=field.get("placeholder", ""),
            id=f"field-{field['key']}"
        )

        # Configure input based on field type
        if self.field_type in ["integer", "number"]:
            self.input.type = self.field_type
            self.input.value = field.get("defaultValue", "")
            
        elif self.field_type == "autocomplete":
            self.input.heldValue = field.get("defaultValue", "")
            self.input.value = str(field.get("defaultValueText", field.get("defaultValue", "")))
            
        elif self.field_type != "boolean":
            self.input.value = field.get("defaultValue", "")

    def on_auto_complete_selected(self, event: AutoComplete.Selected) -> None:
        """Handle autocomplete selection"""
        self.screen.focus_next()
        
        # Find matching option and set held value
        for item in self.field["options"]:
            item_text = str(item.get("text", item["value"]))
            if item_text == str(event.item.main):
                self.input.heldValue = item["value"]
                break

    def compose(self) -> ComposeResult:
        if self.field_type == "hidden":
            # Hidden fields just need a static widget to hold the value
            self.input = Static(id=f"field-{self.field['key']}")
            self.input.heldValue = self.field.get("defaultValue", "")
            yield self.input
            return

        # Visible fields get a container with label and input
        with Container(classes="row", id=f"row-field-{self.field['key']}"):
            yield Label(f"{self.field['title']}", classes="row-label")

            if self.field_type == "autocomplete":
                # Build dropdown items list
                dropdown_items = [
                    DropdownItem(
                        item.get("text", item["value"]),
                        item.get("prefix", item.get("prefix", "")), 
                        item.get("postfix", item.get("postfix", ""))
                    ) for item in self.field["options"]
                ]
                
                yield AutoComplete(
                    self.input,
                    Dropdown(
                        items=dropdown_items,
                        show_on_focus=True,
                        create_option=True
                    ),
                    classes="field-autocomplete",
                    create_action=self.field.get("create_action")
                )

            elif self.field_type == "boolean":
                with Container(classes="switch-group"):
                    yield Label(f"[italic]{self.field['labels'][0]}[/italic]")
                    yield Switch(
                        id=f"field-{self.field['key']}", 
                        value=self.field.get("defaultValue", False)
                    )
                    yield Label(f"[italic]{self.field['labels'][1]}[/italic]")

            else:
                yield self.input
