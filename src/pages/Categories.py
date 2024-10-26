from textual.app import ComposeResult
from textual.widgets import Label, Static
from components.base import BasePage   

class Page(Static):
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        with BasePage(
            pageName="Categories",
            bindings=[],
        ):
            yield Label("Categories")
