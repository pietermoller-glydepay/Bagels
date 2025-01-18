from textual.app import ComposeResult
from textual.containers import Center
from textual.widgets import Static

from bagels.components.bagel import Bagel
from bagels.components.modules.categories import Categories
from bagels.components.modules.people import People
from bagels.managers.accounts import get_accounts_count
from bagels.managers.categories import get_categories_count


class Manager(Static):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="manager-page")
        self.isReady = get_accounts_count() and get_categories_count()

    def on_mount(self) -> None:
        self.app.watch(self.app, "layout", self.on_layout_change)

    # -------------- Helpers ------------- #

    def rebuild(self) -> None:
        pass

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
        # with Static(classes="home-modules-container v"):
        #     with Static(classes="left"):
        #         with Static(id="home-top-container"):
        #             yield self.accounts_module
        #             with Static(id="home-mode-container"):
        #                 yield self.income_mode_module
        #                 yield self.date_mode_module
        #         yield self.insights_module
        #     with Static(classes="right"):
        #         if self.isReady:
        #             yield self.templates_module
        #             yield self.record_module
        #         else:
        if self.isReady:
            with Static(classes="manager-modules-container"):
                yield Static(id="budget-container", classes="module-container")
                yield Categories()
                yield People()
        else:
            with Center():
                yield Bagel()
