
#region Accounts
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Label, Static

from controllers.accounts import get_all_accounts_with_balance


class Accounts(ScrollableContainer):
    can_focus = True
    
    def __init__(self, parent: Static, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="accounts-container", classes="module-container")
        super().__setattr__("border_title", "Accounts (using)")
        self.page_parent = parent
    
    def on_mount(self) -> None:
        pass
    
    #region Builder
    # -------------- Builder ------------- #
    
    def rebuild(self) -> None:
        for account in get_all_accounts_with_balance():
            self.query_one(f"#account-{account.id}-balance").update(str(account.balance))
            acccount_container = self.query_one(f"#account-{account.id}-container")
            scroll = False
            if self.page_parent.mode["accountId"]["defaultValue"] == account.id:
                selected = "selected"
                scroll = True
            else:
                selected = ""
            acccount_container.classes = f"account-container {selected}"
            if scroll:
                self.scroll_to_widget(acccount_container)
        
    #region View
    # --------------- View --------------- #

    def compose(self) -> ComposeResult:
        for account in get_all_accounts_with_balance():
            if self.page_parent.mode["accountId"]["defaultValue"] == account.id:
                selected = "selected"
            else:
                selected = ""
                
            with Container(id=f"account-{account.id}-container", classes=f"account-container {selected}"):
                yield Label(
                    f"{account.name}[italic] {account.description or ''}[/italic]",
                    classes="name",
                    markup=True
                )
                yield Label(str(account.balance), classes="balance", id=f"account-{account.id}-balance")
