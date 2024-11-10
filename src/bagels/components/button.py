from __future__ import annotations

from typing import TYPE_CHECKING, cast

import rich.repr
from rich.cells import cell_len
from rich.console import ConsoleRenderable, RenderableType
from rich.text import Text, TextType

if TYPE_CHECKING:
    from textual.app import RenderResult

from textual import events
from textual.binding import Binding
from textual.geometry import Size
from textual.message import Message
from textual.pad import HorizontalPad
from textual.reactive import reactive
from textual.widget import Widget


class Button(Widget):
    """A simple clickable button."""

    DEFAULT_CSS = """
    Button {
        width: auto;
        height: auto;
        color: $text;

        &:focus {
            text-style: bold reverse;
        }

        &:hover {
            background: $panel-darken-2;
            color: $text;
        }

        &.-active {
            background: $panel;
            tint: $background 30%;
        }
    }
    """

    BINDINGS = [Binding("enter", "press", "Press button", show=False)]

    label: reactive[TextType] = reactive[TextType]("")
    """The text label that appears within the button."""

    class Pressed(Message):
        """Event sent when a Button is pressed."""

        def __init__(self, button: Button) -> None:
            self.button: Button = button
            """The button that was pressed."""
            super().__init__()

        @property
        def control(self) -> Button:
            """An alias for button."""
            return self.button

    def __init__(
        self,
        label: TextType | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        """Create a Button widget.

        Args:
            label: The text that appears within the button.
            name: The name of the button.
            id: The ID of the button in the DOM.
            classes: The CSS classes of the button.
            disabled: Whether the button is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        if label is None:
            label = self.css_identifier_styled

        self.label = label
        self.active_effect_duration = 0.2

    def get_content_width(self, container: Size, viewport: Size) -> int:
        try:
            return max([cell_len(line) for line in self.label.plain.splitlines()]) + 2
        except ValueError:
            # Empty string label
            return 2

    def validate_label(self, label: TextType) -> Text:
        """Parse markup for self.label"""
        if isinstance(label, str):
            return Text.from_markup(label)
        return label

    def render(self) -> RenderResult:
        assert isinstance(self.label, Text)
        label = self.label.copy()
        label.stylize_before(self.rich_style)
        return HorizontalPad(
            label,
            1,
            1,
            self.rich_style,
            self._get_rich_justify() or "center",
        )

    def post_render(self, renderable: RenderableType) -> ConsoleRenderable:
        return cast(ConsoleRenderable, renderable)

    async def _on_click(self, event: events.Click) -> None:
        event.stop()
        if not self.has_class("-active"):
            self.press()

    def press(self) -> Button:
        """Animate the button and send the Pressed message."""
        if self.disabled or not self.display:
            return self
        self._start_active_affect()
        self.post_message(Button.Pressed(self))
        return self

    def _start_active_affect(self) -> None:
        """Start a small animation to show the button was clicked."""
        if self.active_effect_duration > 0:
            self.add_class("-active")
            self.set_timer(
                self.active_effect_duration, lambda: self.remove_class("-active")
            )

    def action_press(self) -> None:
        """Activate a press of the button."""
        if not self.has_class("-active"):
            self.press()
