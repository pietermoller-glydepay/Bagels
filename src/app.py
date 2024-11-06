from rich.console import Group
from rich.text import Text
from textual import events, on
from textual.app import App as TextualApp
from textual.app import ComposeResult, SystemCommand
from textual.binding import Binding
from textual.command import CommandPalette
from textual.containers import Container
from textual.css.query import NoMatches
from textual.geometry import Size
from textual.reactive import Reactive, reactive
from textual.signal import Signal
from textual.widgets import Footer, Header, Label, Tab, Tabs
from textual.widgets.text_area import TextAreaTheme

from home import Home
from models.database.app import init_db
from provider import AppProvider
from queries.categories import create_default_categories
from themes import BUILTIN_THEMES, Theme
from utils.user_host import get_user_host_string


class App(TextualApp):
    
    CSS_PATH = "index.tcss"
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]
    COMMANDS = {AppProvider}

    theme: Reactive[str] = reactive("galaxy", init=False)
    """The currently selected theme. Changing this reactive should
    trigger a complete refresh via the `watch_theme` method."""
    layout: Reactive[str] = reactive("h")
    
    
    #region init
    def __init__(self):
        # Initialize available themes with a default
        available_themes: dict[str, Theme] = {"galaxy": BUILTIN_THEMES["galaxy"]}
        available_themes |= BUILTIN_THEMES
        self.themes = available_themes
        super().__init__()
    
    
    def on_mount(self) -> None:
        self.theme_change_signal = Signal[Theme](self, "theme-changed")
    
    # used by the textual app to get the theme variables
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
    
    #region bindings
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
    
    #region theme 
    # --------------- theme -------------- #
    def watch_theme(self, theme: str | None) -> None:
        self.refresh_css(animate=False)
        self.screen._update_styles()
        if theme:
            theme_object = self.themes[theme]
            self.theme_change_signal.publish(theme_object)
    
    @on(CommandPalette.Opened)
    def palette_opened(self) -> None:
        self._original_theme = self.theme
    
    @on(CommandPalette.OptionHighlighted)
    def palette_option_highlighted(
        self, event: CommandPalette.OptionHighlighted
    ) -> None:
        prompt: Group = event.highlighted_event.option.prompt
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

    #region hooks
    # --------------- hooks -------------- #
    
    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        if event.tab.id.startswith("t"):
            activeIndex = int(event.tab.id.removeprefix("t")) - 1
            try:
                currentContent = self.query_one(".content")
                currentContent.remove()
            except NoMatches:
                pass
            page_class = self.PAGES[activeIndex]["class"]
            page_instance = page_class(classes="content")
            self.mount(page_instance)
    
    def on_resize(self, event: events.Resize) -> None:
        console_size: Size = self.console.size
        aspect_ratio = (console_size.width / 2) / console_size.height
        if aspect_ratio < 1:
            self.layout = "v"
        else:
            self.layout = "h"
    
    #region callbacks
    # --------------- Callbacks ------------ #

    def action_goToTab(self, tab_number: int) -> None:
        """Go to the specified tab."""
        tabs = self.query_one(Tabs)
        tabs.active = f"t{tab_number}"

    def action_quit(self) -> None:
        self.exit()
    
    def action_create_default_categories(self) -> None:
        create_default_categories()
    
    #region view
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        with Container(classes="header"):
            yield Label("↪ Expense Tracker", classes="title")
            yield Label("0.1.0", classes="version")
            yield Label(get_user_host_string(), classes="user")
        yield Home(classes="content")
        yield Footer()

if __name__ == "__main__":
    init_db() 
    app = App()
    app.run()


    
