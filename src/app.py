from typing import Iterable

from textual.app import App as TextualApp
from textual.app import ComposeResult, SystemCommand
from textual.binding import Binding
from textual.css.query import NoMatches
from textual.screen import Screen
from textual.widgets import Footer, Header, Tab, Tabs

# from controllers.categories import create_default_categories
from controllers.categories import create_default_categories
from models.database.app import init_db
from pages import Accounts, Categories, Home, Receivables, Reports, Settings


class App(TextualApp):
    
    CSS_PATH = "index.scss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit")
    ]

    PAGES = [
    {
        "name": "Home",
        "widget": Home.Page(classes="content")
    },
    {
        "name": "Receivables",
        "widget": Receivables.Page(classes="content")
    },
    {
        "name": "Reports",
        "widget": Reports.Page(classes="content")
    },
    {
        "name": "Accounts",
        "widget": Accounts.Page(classes="content")
    },
    {
        "name": "Categories",
        "widget": Categories.Page(classes="content")
    },
    {
        "name": "Settings",
        "widget": Settings.Page(classes="content")
    }
    ]
    
    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)  
        yield SystemCommand("Import default categories", "Import default categories", create_default_categories)  

    # ---------- Bindings helper ---------- #
    def newBinding(self, binding: Binding) -> None:
        self._bindings.key_to_bindings.setdefault(binding.key, []).append(binding)
        self.refresh_bindings()
    
    def checkBindingExists(self, key: str) -> bool:
        return key in self._bindings.key_to_bindings

    def removeBinding(self, key: str) -> None:
        binding = self._bindings.key_to_bindings.pop(key, None)
        if binding:
            self.refresh_bindings()
    
    # ------------- Callbacks ------------ #
    def on_mount(self) -> None:
        self.query_one(Tabs).focus()
        self.title = "Tallet"

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        activeIndex = int(event.tab.id.removeprefix("t")) - 1
        try:
            currentContent = self.query_one(".content")
            currentContent.remove()
        except NoMatches:
            pass
        self.mount(self.PAGES[activeIndex]["widget"])

    def action_goToTab(self, tab_number: int) -> None:
        """Go to the specified tab."""
        tabs = self.query_one(Tabs)
        tabs.active = f"t{tab_number}"

    def action_quit(self) -> None:
        self.exit()

    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        yield Header()
        yield Tabs(*[Tab(f"{page["name"]} [{index+1}]", id=f"t{index + 1}") for index, page in enumerate(self.PAGES)])
        yield Footer()
    

if __name__ == "__main__":
    init_db() # fix issue with home screen accessing accounts before db initialized
    app = App()
    app.run()


    
