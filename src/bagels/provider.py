from functools import partial
from typing import TYPE_CHECKING, cast

from textual.command import DiscoveryHit, Hit, Hits, Provider
from textual.types import IgnoreReturnCallbackType

from bagels.models.database.app import wipe_database
from bagels.managers.samples import create_sample_entries

if TYPE_CHECKING:
    from bagels.app import App


class AppProvider(Provider):
    @property
    def commands(
        self,
    ) -> tuple[tuple[str, IgnoreReturnCallbackType, str, bool], ...]:
        app = self.app

        commands_to_show: list[tuple[str, IgnoreReturnCallbackType, str, bool]] = [
            ("app: quit", app.action_quit, "Quit App", True),
            (
                "dev: create sample entries",
                self._action_create_sample_entries,
                "Create sample entries defined in static/sample_entries.yaml",
                False,
            ),
            (
                "dev: wipe database",
                self._action_wipe_database,
                "Delete everything from the database",
                False,
            ),
            *self.get_theme_commands(),
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
        app = self.app
        return tuple(self.get_theme_command(theme) for theme in app.themes)

    def get_theme_command(
        self, theme_name: str
    ) -> tuple[str, IgnoreReturnCallbackType, str, bool]:
        return (
            f"theme: {theme_name}",
            partial(self.app.command_theme, theme_name),
            f"Set the theme to {theme_name}",
            True,
        )

    @property
    def app(self) -> "App":
        return cast("App", self.screen.app)

    def _action_create_sample_entries(self) -> None:
        create_sample_entries()
        self.app.refresh(layout=True, recompose=True)

    def _action_wipe_database(self) -> None:
        wipe_database()
        self.app.refresh(layout=True, recompose=True)
        # def check_delete(result) -> None:

        # self.app.push_screen(ConfirmationModal(
        #     message="Are you sure you want to wipe the database?",
        # ), callback=check_delete)
