from datetime import datetime, timedelta

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Static

from components.base import BasePage
from components.modules.insights import Insights
from components.modules.records import Records
from controllers.accounts import (get_accounts_count,
                                  get_all_accounts_with_balance)
from controllers.categories import get_categories_count
from utils.format import format_period_to_readable
from utils.forms import RecordForm


#region Page
class Page(Static):
    filter = {
        "offset": 0,
        "offset_type": "month",
    }
    
    BINDINGS = [
        ("left", "prev_month", "Previous Month"),
        ("right", "next_month", "Next Month"),
        (".", "cycle_offset_type", "Cycle filter type"),
    ]
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="home-page")
        self.isReady = get_accounts_count() and get_categories_count()
        
    
    # -------------- Helpers ------------- #
    
    def rebuild(self) -> None:
        self.record_module.rebuild()
        self.insights_module.rebuild()
    
    def update_filter_label(self, label: Label) -> None:
        string = format_period_to_readable(self.filter)
        label.update(string)
        
    #region Callbacks
    # ------------- Callbacks ------------ #
    
    def action_prev_month(self) -> None:
        self.filter["offset"] -= 1
        self.rebuild()
    
    def action_next_month(self) -> None:
        if self.filter["offset"] < 0:
            self.filter["offset"] += 1
            self.rebuild()
        else:
            self.app.bell()
    
    def action_cycle_offset_type(self, direction: str = "forward") -> None:
        # Define the cycle order
        cycle_order = ["day", "week", "month", "year"]
        
        # Get current index
        current_index = cycle_order.index(self.filter["offset_type"])
        
        # Calculate next index based on direction
        if direction == "forward":
            next_index = (current_index + 1) % len(cycle_order)
        else:
            next_index = (current_index - 1) % len(cycle_order)
            
        # Update filter type
        self.filter["offset_type"] = cycle_order[next_index]
        
        # Refresh table
        self.rebuild()
    
    #region View
    # --------------- View --------------- #
    
    def compose(self) -> ComposeResult:
        self.basePage = BasePage(
            pageName="Home",
            bindings =[]
            # bindings=[
            #     (CONFIG.hotkeys.new, "new_record", "Add", self.action_new_record),
            #     (CONFIG.hotkeys.delete, "delete_record", "Delete", self.action_delete_record),
            #     (CONFIG.hotkeys.edit, "edit_record", "Edit", self.action_edit_record),
            #     (CONFIG.hotkeys.home.new_transfer, "new_transfer", "Transfer", self.action_new_transfer),
            #     (CONFIG.hotkeys.home.toggle_splits, "toggle_splits", "Toggle Splits", self.action_toggle_splits),
            #     (CONFIG.hotkeys.home.display_by_person, "display_by_person", "Display by Person", self.action_display_by_person),
            #     (CONFIG.hotkeys.home.display_by_date, "display_by_date", "Display by Date", self.action_display_by_date),
            #     ("left", "prev_month", "Previous Month", self.action_prev_month),
            #     ("right", "next_month", "Next Month", self.action_next_month),
            # ],
        )
        with self.basePage:
            # accountsContainer = Container(id="accounts-container", classes="module-container")
            # accountsContainer.border_subtitle = "Accounts"
            # with accountsContainer:
            #     with Horizontal(classes="home-accounts-list"):
            #         for account in get_all_accounts_with_balance():
            #             with Container(classes="account-container"):
            #                 yield Label(
            #                     f"[bold]{account.name}[/bold][italic] {account.description or ''}[/italic]",
            #                     classes="account-name",
            #                     markup=True
            #                 )
            #                 yield Label(
            #                     f"${account.balance}",
            #                     classes="account-balance",
            #                     id=f"account-{account.id}-balance"
            #                 )
            if not self.isReady:
                yield Label(
                    "Please create at least one account and one category to get started.",
                    classes="label-empty"
                )
            if self.isReady:
                self.record_module = Records(parent=self)
                self.insights_module = Insights(parent=self)
                yield self.record_module
                yield self.insights_module
