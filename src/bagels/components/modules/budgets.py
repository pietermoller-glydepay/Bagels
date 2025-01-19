from textual.app import ComposeResult
from textual.widgets import Static


class Budgets(Static):
    can_focus = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args, **kwargs, id="budgets-container", classes="module-container"
        )
        super().__setattr__("border_title", "Budget")

    # --------------- Hooks -------------- #

    def on_mount(self) -> None:
        self.rebuild()

    # region Builders
    # ------------- Builders ------------- #

    def rebuild(self) -> None:
        pass

    # region View
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        yield Static("Budgets")
