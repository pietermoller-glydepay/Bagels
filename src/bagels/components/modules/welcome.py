from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, MarkdownViewer, Rule, Static
from bagels.bagel import get_string, pprint, render_frame, theta_spacing, phi_spacing


class Welcome(Static):

    A = B = 1
    can_focus = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="welcome-container")
        file_path = Path(__file__).parent.parent.parent / "static" / "welcome.md"
        with open(file_path, "r") as file:
            self.welcome_text = file.read()

    def on_mount(self) -> None:
        self.set_interval(1 / 10, self.update_bagel)

    def update_bagel(self) -> None:
        bagel = self.query_one("#bagel")
        self.A += theta_spacing
        self.B += phi_spacing
        bagel.update(get_string(render_frame(self.A, 1)))

    def compose(self) -> ComposeResult:

        with Container(classes="text-container"):
            yield MarkdownViewer(self.welcome_text, show_table_of_contents=False)
        with Container(classes="bagel-container"):
            yield Label(id="bagel")
