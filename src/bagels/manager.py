from textual.app import ComposeResult
from textual.containers import Center
from textual.widgets import Static

from bagels.components.bagel import Bagel
from bagels.components.modules.budgets import Budgets
from bagels.components.modules.categories import Categories
from bagels.components.modules.people import People
from bagels.components.modules.spending import Spending
from bagels.managers.accounts import get_accounts_count
from bagels.managers.categories import get_categories_count


class Manager(Static):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="manager-page")
        self.isReady = get_accounts_count() and get_categories_count()
        self.spending_module = Spending()
        self.categories_module = Categories()
        self.budgets_module = Budgets()
        self.people_module = People()

    def on_mount(self) -> None:
        self.app.watch(self.app, "layout", self.on_layout_change)

    # -------------- Helpers ------------- #

    def rebuild(self) -> None:
        if self.isReady:
            self.spending_module.rebuild()
            self.categories_module.rebuild()
            self.budgets_module.rebuild()
            self.people_module.rebuild()

    # region Callbacks
    # ------------- Callbacks ------------ #

    def on_layout_change(self, layout: str) -> None:
        pass
        # layout_container = self.query(".home-modules-container")
        # if len(layout_container) > 0:
        #     layout_container[0].set_classes(f"home-modules-container {layout}")

    # region View
    # --------------- View --------------- #

    def compose(self) -> ComposeResult:
        if self.isReady:
            with Static(classes="manager-modules-container"):
                yield self.spending_module
                yield self.categories_module
                yield self.budgets_module
                yield self.people_module
        else:
            with Center():
                yield Bagel()
