from rich.console import Group
from rich.text import Text
from textual import on
from textual.app import App as TextualApp
from textual.app import ComposeResult, SystemCommand
from textual.binding import Binding
from textual.command import CommandPalette
from textual.containers import Container
from textual.css.query import NoMatches
from textual.reactive import Reactive, reactive
from textual.signal import Signal
from textual.widgets import Footer, Header, Label, Tab, Tabs
from textual.widgets.text_area import TextAreaTheme

from controllers.categories import create_default_categories
from models.database.app import init_db
from pages import Accounts, Categories, Home, Receivables, Reports
from provider import AppProvider
from themes import BUILTIN_THEMES, Theme
from utils.user_host import get_user_host_string


class App(TextualApp):
    
    CSS_PATH = "index.tcss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit")
    ]
    COMMANDS = {AppProvider}

    PAGES = [
        {
            "name": "Home",
            "class": Home.Page,
        },
        {
            "name": "Receivables",
            "class": Receivables.Page,
        },
        {
            "name": "Reports",
            "class": Reports.Page,
        },
        {
            "name": "Accounts",
            "class": Accounts.Page,
        },
        {
            "name": "Categories",
            "class": Categories.Page,
        }
    ]

    theme: Reactive[str] = reactive("galaxy", init=False)
    """The currently selected theme. Changing this reactive should
    trigger a complete refresh via the `watch_theme` method."""
    
    def __init__(self):
        # Initialize available themes with a default
        available_themes: dict[str, Theme] = {"galaxy": BUILTIN_THEMES["galaxy"]}
        available_themes |= BUILTIN_THEMES
        self.themes = available_themes
        super().__init__()
    
    def on_mount(self) -> None:
        self.theme_change_signal = Signal[Theme](self, "theme-changed")
    
    def get_css_variables(self) -> dict[str, str]:
        if self.theme:
            theme = self.themes.get(self.theme)
            if theme:
                color_system = theme.to_color_system().generate()
            else:
                color_system = {}
        else:
            color_system = {}
        return {**super().get_css_variables(), **color_system}

    def command_theme(self, theme: str) -> None:
        self.theme = theme
        self.notify(
            f"Theme is now [b]{theme!r}[/].", title="Theme updated", timeout=2.5
        )
    
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
    
    # --------------- Hooks -------------- #
        
    def watch_theme(self, theme: str | None) -> None:
        self.refresh_css(animate=False)
        self.screen._update_styles()
        if theme:
            theme_object = self.themes[theme]
            # if syntax := getattr(theme_object, "syntax", None):
            #     if isinstance(syntax, str):
            #         valid_themes = {
            #             theme.name for theme in TextAreaTheme.builtin_themes()
            #         }
            #         valid_themes.add("posting")
            #         if syntax not in valid_themes:
            #             # Default to the posting theme for text areas
            #             # if the specified theme is invalid.
            #             theme_object.syntax = "posting"
            #             self.notify(
            #                 f"Theme {theme!r} has an invalid value for 'syntax': {syntax!r}. Defaulting to 'posting'.",
            #                 title="Invalid theme",
            #                 severity="warning",
            #                 timeout=7,
            #             )

            self.theme_change_signal.publish(theme_object)
    
    @on(CommandPalette.Opened)
    def palette_opened(self) -> None:
        # If the theme preview is disabled, don't record the theme being used
        # before the palette is opened.
        # if not self.settings.command_palette.theme_preview:
        #     return

        # Record the theme being used before the palette is opened.
        self._original_theme = self.theme
    
    @on(CommandPalette.OptionHighlighted)
    def palette_option_highlighted(
        self, event: CommandPalette.OptionHighlighted
    ) -> None:
        # If the theme preview is disabled, don't update the theme when an option
        # is highlighted.
        # if not self.settings.command_palette.theme_preview:
        #     return

        prompt: Group = event.highlighted_event.option.prompt
        # TODO: This is making quite a lot of assumptions. Fragile, but the only
        # way I can think of doing it given the current Textual APIs.
        command_name = prompt.renderables[0]
        if isinstance(command_name, Text):
            command_name = command_name.plain
        command_name = command_name.strip()
        if ":" in command_name:
            name, value = command_name.split(":", maxsplit=1)
            name = name.strip()
            value = value.strip()
            if name == "theme":
                if value in self.themes:
                    self.theme = value
            else:
                self.theme = self._original_theme
        
    @on(CommandPalette.Closed)
    def palette_closed(self, event: CommandPalette.Closed) -> None:
        # If we closed with a result, that will be handled by the command
        # being triggered. However, if we closed the palette with no result
        # then make sure we revert the theme back.
        # if not self.settings.command_palette.theme_preview:
        #     return
        if not event.option_selected:
            self.theme = self._original_theme

    # --------------- Callbacks ------------ #
    
    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        activeIndex = int(event.tab.id.removeprefix("t")) - 1
        try:
            currentContent = self.query_one(".content")
            currentContent.remove()
        except NoMatches:
            pass
        page_class = self.PAGES[activeIndex]["class"]
        page_instance = page_class(classes="content")
        self.mount(page_instance)

    def action_goToTab(self, tab_number: int) -> None:
        """Go to the specified tab."""
        tabs = self.query_one(Tabs)
        tabs.active = f"t{tab_number}"

    def action_quit(self) -> None:
        self.exit()
    
    def action_create_default_categories(self) -> None:
        create_default_categories()

    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        with Container(classes="header"):
            yield Label("↪ Expense Tracker", classes="title")
            yield Label("0.1.0", classes="version")
            yield Label(get_user_host_string(), classes="user")
        yield Tabs(*[Tab(f"{page["name"]} [{index+1}]", id=f"t{index + 1}") for index, page in enumerate(self.PAGES)])
        yield Footer()
    

if __name__ == "__main__":
    init_db() # fix issue with home screen accessing accounts before db initialized
    app = App()
    app.run()


    
