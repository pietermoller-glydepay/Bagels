from datetime import datetime
from textual.app import App as TextualApp, ComposeResult
from textual.widgets import Footer, Tabs, Tab, Header
from textual.binding import Binding
from textual.css.query import NoMatches
from rich import print as rprint
from pages import Home, Settings, Reports, Accounts, Categories, Receivables
from models.database.app import init_db

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


    # ---------- Bindings helper ---------- #
    def newBinding(self, binding: Binding) -> None:
        self._bindings.key_to_bindings.setdefault(binding.key, []).append(binding)
        self.refresh_bindings()

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
    app = App()
    init_db()
    app.run()


    
