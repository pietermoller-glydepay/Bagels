from textual.binding import Binding
from textual.app import ComposeResult
from textual.widgets import Static
from typing import Callable

class BasePage(Static):
    def __init__(self, pageName: str, bindings: list[tuple[str, str, str, Callable]], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pageName = pageName
        self.bindings = [Binding(key=binding[0], action=binding[1], description=binding[2]) for binding in bindings]
        for binding, func in zip(self.bindings, [binding[3] for binding in bindings]):
            setattr(self.app, f"action_{binding.action}", func)

    def on_mount(self) -> None:
        app = self.app

        for binding in self.bindings:
            app.newBinding(binding)

        for i, page in enumerate(app.PAGES):
            if page["name"] != self.pageName:
                app.newBinding(Binding(key=str(i + 1), action=f"goToTab({i + 1})", description=page["name"]))

    def on_unmount(self) -> None:
        app = self.app
        for binding in self.bindings:
            app.removeBinding(binding.key)
        for i, page in enumerate(app.PAGES):
            if page["name"] != self.pageName:
                app.removeBinding(str(i + 1))