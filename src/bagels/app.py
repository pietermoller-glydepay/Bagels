from importlib.metadata import metadata

from rich.console import Group
from rich.text import Text
from textual import events, log, on
from textual.app import App as TextualApp
from textual.app import ComposeResult
from textual.command import CommandPalette
from textual.containers import Container
from textual.content import Content
from textual.css.query import NoMatches
from textual.geometry import Size
from textual.reactive import Reactive, reactive
from textual.signal import Signal
from textual.widget import Widget
from textual.widgets import Footer, Label, Tabs

from bagels.components.jump_overlay import JumpOverlay
from bagels.components.jumper import Jumper
from bagels.config import CONFIG, write_state
from bagels.home import Home
from bagels.modals.categories import CategoriesModal
from bagels.provider import AppProvider
from bagels.themes import BUILTIN_THEMES, Theme
from bagels.utils.user_host import get_user_host_string


class App(TextualApp):

    CSS_PATH = "index.tcss"
    BINDINGS = [
        (CONFIG.hotkeys.toggle_jump_mode, "toggle_jump_mode", "Jump Mode"),
        (CONFIG.hotkeys.home.categories, "go_to_categories", "Categories"),
        ("ctrl+q", "quit", "Quit"),
    ]
    COMMANDS = {AppProvider}

    app_theme: Reactive[str] = reactive(CONFIG.state.theme, init=False)
    """The currently selected theme. Changing this reactive should
    trigger a complete refresh via the `watch_theme` method."""
    layout: Reactive[str] = reactive("h")
    """The current layout of the app."""
    _jumping: Reactive[bool] = reactive(False, init=False, bindings=True)
    """True if 'jump mode' is currently active, otherwise False."""

    # region init
    def __init__(self):
        # Initialize available themes with a default
        available_themes: dict[str, Theme] = {"galaxy": BUILTIN_THEMES["galaxy"]}
        available_themes |= BUILTIN_THEMES
        self.themes = available_themes
        super().__init__()

        # Get package metadata directly
        meta = metadata("bagels")
        self.project_info = {"name": meta["Name"], "version": meta["Version"]}

    def on_mount(self) -> None:
        # --------------- theme -------------- #
        self.theme_change_signal = Signal[Theme](self, "theme-changed")
        # -------------- jumper -------------- #
        self.jumper = Jumper(
            {
                "accounts-container": "a",
                "insights-container": "i",
                "records-container": "r",
                "templates-container": "t",
                # "incomemode-container": "v",
                "datemode-container": "p",
            },
            screen=self.screen,
        )

    # used by the textual app to get the theme variables
    def get_css_variables(self) -> dict[str, str]:
        if self.app_theme:
            theme = self.themes.get(self.app_theme)
            if theme:
                color_system = theme.to_color_system().generate()
            else:
                color_system = {}
        else:
            color_system = {}
        return {**super().get_css_variables(), **color_system}

    def command_theme(self, theme: str) -> None:
        self.app_theme = theme
        self.notify(
            f"Theme is now [b]{theme!r}[/].", title="Theme updated", timeout=2.5
        )
        write_state("theme", theme)

    # region theme
    # --------------- theme -------------- #
    def watch_app_theme(self, theme: str | None) -> None:
        self.refresh_css(animate=False)
        self.screen._update_styles()
        if theme:
            theme_object = self.themes[theme]
            self.theme_change_signal.publish(theme_object)

    @on(CommandPalette.Opened)
    def palette_opened(self) -> None:
        self._original_theme = self.app_theme

    @on(CommandPalette.OptionHighlighted)
    def palette_option_highlighted(
        self, event: CommandPalette.OptionHighlighted
    ) -> None:
        prompt: Content = event.highlighted_event.option.prompt
        command_name = prompt.plain.split("\n")[0]
        if ":" in command_name:
            name, value = command_name.split(":", maxsplit=1)
            name = name.strip()
            value = value.strip()
            if name == "theme":
                if value in self.themes:
                    self.app_theme = value
            else:
                self.app_theme = self._original_theme

    @on(CommandPalette.Closed)
    def palette_closed(self, event: CommandPalette.Closed) -> None:
        # If we closed with a result, that will be handled by the command
        # being triggered. However, if we closed the palette with no result
        # then make sure we revert the theme back.
        # if not self.settings.command_palette.theme_preview:
        #     return
        if not event.option_selected:
            self.app_theme = self._original_theme

    # region jumper
    # -------------- jumper -------------- #
    def action_toggle_jump_mode(self) -> None:
        self._jumping = not self._jumping

    def watch__jumping(self, jumping: bool) -> None:
        focused_before = self.focused
        if focused_before is not None:
            self.set_focus(None, scroll_visible=False)

        def handle_jump_target(target: str | Widget | None) -> None:
            if isinstance(target, str):
                try:
                    target_widget = self.screen.query_one(f"#{target}")
                except NoMatches:
                    log.warning(
                        f"Attempted to jump to target #{target}, but it couldn't be found on {self.screen!r}"
                    )
                else:
                    if target_widget.focusable:
                        self.set_focus(target_widget)
                    else:
                        target_widget.post_message(
                            events.Click(0, 0, 0, 0, 0, False, False, False)
                        )

            elif isinstance(target, Widget):
                self.set_focus(target)
            else:
                # If there's no target (i.e. the user pressed ESC to dismiss)
                # then re-focus the widget that was focused before we opened
                # the jumper.
                if focused_before is not None:
                    self.set_focus(focused_before, scroll_visible=False)

        self.clear_notifications()
        self.push_screen(JumpOverlay(self.jumper), callback=handle_jump_target)

    # region hooks
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

    # region callbacks
    # --------------- Callbacks ------------ #

    def action_goToTab(self, tab_number: int) -> None:
        """Go to the specified tab."""
        tabs = self.query_one(Tabs)
        tabs.active = f"t{tab_number}"

    def action_quit(self) -> None:
        self.exit()

    def action_go_to_categories(self) -> None:
        self.push_screen(CategoriesModal(), callback=self.on_categories_dismissed)

    def on_categories_dismissed(self, _) -> None:
        self.app.refresh(recompose=True)

    # region view
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        with Container(classes="header"):
            yield Label(f"↪ {self.project_info['name']}", classes="title")
            yield Label(self.project_info["version"], classes="version")
            yield Label(get_user_host_string(), classes="user")
        yield Home(classes="content")
        yield Footer()
