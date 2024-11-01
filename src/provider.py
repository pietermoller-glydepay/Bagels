from functools import partial
from typing import TYPE_CHECKING, cast

from textual.command import DiscoveryHit, Hit, Hits, Provider
from textual.types import IgnoreReturnCallbackType

if TYPE_CHECKING:
    from app import App


class AppProvider(Provider):
    @property
    def commands(
        self,
    ) -> tuple[tuple[str, IgnoreReturnCallbackType, str, bool], ...]:
        app = self.posting

        commands_to_show: list[tuple[str, IgnoreReturnCallbackType, str, bool]] = [
            *self.get_theme_commands(),
            ("app: quit", app.action_quit, "Quit Posting", True),
        ]

        return tuple(commands_to_show)

    async def discover(self) -> Hits:
        """Handle a request for the discovery commands for this provider.

        Yields:
            Commands that can be discovered.
        """
        for name, runnable, help_text, show_discovery in self.commands:
            if show_discovery:
                yield DiscoveryHit(
                    name,
                    runnable,
                    help=help_text,
                )

    async def search(self, query: str) -> Hits:
        """Handle a request to search for commands that match the query.

        Args:
            query: The user input to be matched.

        Yields:
            Command hits for use in the command palette.
        """
        matcher = self.matcher(query)
        for name, runnable, help_text, _ in self.commands:
            if (match := matcher.match(name)) > 0:
                yield Hit(
                    match,
                    matcher.highlight(name),
                    runnable,
                    help=help_text,
                )

    def get_theme_commands(
        self,
    ) -> tuple[tuple[str, IgnoreReturnCallbackType, str, bool], ...]:
        posting = self.posting
        return tuple(self.get_theme_command(theme) for theme in posting.themes)

    def get_theme_command(
        self, theme_name: str
    ) -> tuple[str, IgnoreReturnCallbackType, str, bool]:
        return (
            f"theme: {theme_name}",
            partial(self.posting.command_theme, theme_name),
            f"Set the theme to {theme_name}",
            False,
        )

    @property
    def posting(self) -> "App":
        return cast("App", self.screen.app)
