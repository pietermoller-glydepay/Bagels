
#region Accounts
from textual import events
from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Label, Static

from components.modals import InputModal
from config import CONFIG
from queries.accounts import (create_account, delete_account,
                              get_all_accounts_with_balance, update_account)
from utils.account_forms import AccountForm


class AccountMode(ScrollableContainer):
    BINDINGS = [
        (CONFIG.hotkeys.new, "new", "Add"),
        (CONFIG.hotkeys.delete, "delete", "Delete"),
        (CONFIG.hotkeys.edit, "edit", "Edit"),
    ]
    
    can_focus = True
    
    def __init__(self, parent: Static, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="accounts-container", classes="module-container")
        super().__setattr__("border_title", "Accounts (using)")
        super().__setattr__("border_subtitle", f"{CONFIG.hotkeys.home.select_prev_account} {CONFIG.hotkeys.home.select_next_account}")
        self.page_parent = parent
        self.account_form = AccountForm()
    def on_mount(self) -> None:
        self.rebuild()
    
    #region Builder
    # -------------- Builder ------------- #
    
    def rebuild(self) -> None:
        for account in get_all_accounts_with_balance():
            # Update balance
            self.query_one(f"#account-{account.id}-balance").update(str(account.balance))
            
            # Update account container classes
            account_container = self.query_one(f"#account-{account.id}-container")
            selected = "selected" if self.page_parent.mode["accountId"]["defaultValue"] == account.id else ""
            account_container.classes = f"account-container {selected}"
            
            # Update name/description label
            name_label = self.query_one(f"#account-{account.id}-name")
            name_label.update(account.name)
            description_label = self.query_one(f"#account-{account.id}-description")
            description_label.update(account.description)
            
            # Scroll to selected account
            if selected:
                self.scroll_to_widget(account_container)
                
    #region Callbacks
    # ------------- Callbacks ------------ #
    
    def on_key(self, event: events.Key) -> None:
        if event.key == "up":
            self.page_parent.action_select_prev_account()
        elif event.key == "down":
            self.page_parent.action_select_next_account()
    
    #region cud
    # ---------------- cud --------------- #
    
    def action_new(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_account(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                self.app.notify(title="Success", message=f"Account {result['name']} created", severity="information", timeout=3)
                self.page_parent.rebuild()
        account_form = self.account_form.get_form()
        self.app.push_screen(InputModal("New Account", account_form), callback=check_result)

    def action_delete(self) -> None:
        # def check_delete(result: bool) -> None:
        #     if result:
        #         delete_account(self.current_row)
        #         self.app.notify(title="Success", message=f"Deleted account", severity="information", timeout=3)
        #         self._build_table()
        # if self.current_row:
        #     self.app.push_screen(ConfirmationModal("Are you sure you want to delete this account? Your existing transactions will not be deleted."), check_delete)
        # else:
        #     self._notify_no_accounts()
        pass
    
    def action_edit(self) -> None:
        id = self.page_parent.mode["accountId"]["defaultValue"]
        def check_result(result: bool) -> None:
            if result:
                try:
                    update_account(id, result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                self.app.notify(title="Success", message=f"Account {result['name']} updated", severity="information", timeout=3)
                self.page_parent.rebuild()
        
        if id:
            filled_account_form = self.account_form.get_filled_form(id)
            self.app.push_screen(InputModal("Edit Account", filled_account_form), callback=check_result)
        else:
            self.app.notify(title="Error", message="No account selected", severity="error", timeout=3)
        
    #region View
    # --------------- View --------------- #

    def compose(self) -> ComposeResult:
        for account in get_all_accounts_with_balance():
            with Container(id=f"account-{account.id}-container", classes="account-container"):
                with Container(classes="left-container"):
                    yield Label(
                        "",  # Will be populated in rebuild()
                        classes="name",
                        id=f"account-{account.id}-name"
                    )
                    yield Label(
                        "",  # Will be populated in rebuild()
                        classes="description",
                        id=f"account-{account.id}-description"
                    )
                yield Label("", classes="balance", id=f"account-{account.id}-balance")
