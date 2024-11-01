from typing import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Static


class BasePage(Static):
    def __init__(self, pageName: str, bindings: list[tuple[str, str, str, Callable]], *args, **kwargs):
        super().__init__(id=pageName, classes="base-page", *args, **kwargs)
        self.pageName = pageName
        self.bindings = [Binding(key=binding[0], action=binding[1], description=binding[2]) for binding in bindings]
        
        for binding, func in zip(self.bindings, [binding[3] for binding in bindings]):
            setattr(self.app, f"action_{binding.action}", func)
            # register functions to the main app

    def on_mount(self) -> None:
        app = self.app

        for binding in self.bindings:
            if app.checkBindingExists(binding.key):
                app.removeBinding(binding.key)
            app.newBinding(binding) # register custom bindings to app

        for i, page in enumerate(app.PAGES): # load change page bindings
            if page["name"] != self.pageName:
                app.newBinding(Binding(key=str(i + 1), action=f"goToTab({i + 1})", description=page["name"], show=False))
    
    def on_unmount(self) -> None:
        for binding in self.bindings:
            self.app.removeBinding(binding.key)
    
    def newBinding(self, key: str, action: str, description: str, func: Callable):
        self.app.newBinding(Binding(key=key, action=action, description=description))
        setattr(self.app, f"action_{action}", func)
    
    def removeBinding(self, key: str):
        self.app.removeBinding(key)