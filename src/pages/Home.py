from datetime import datetime

from textual.app import ComposeResult
from textual.reactive import Reactive
from textual.widgets import Label, Static

from components.base import BasePage
from components.modules.accounts import Accounts
from components.modules.datemode import DateMode
from components.modules.incomemode import IncomeMode
from components.modules.insights import Insights
from components.modules.records import Records
from config import CONFIG
from controllers.accounts import get_accounts_count, get_all_accounts
from controllers.categories import get_categories_count
from utils.format import format_period_to_readable


#region Page
class Page(Static):
    filter = {
        "offset": 0,
        "offset_type": "month",
    }
    
    BINDINGS = [
        ("left", "prev_month", "Previous Month"),
        ("right", "next_month", "Next Month"),
        (CONFIG.hotkeys.home.cycle_offset_type, "cycle_offset_type", "Filter"),
        (CONFIG.hotkeys.home.toggle_income_mode, "toggle_income_mode", "Income/Expense"),
        (CONFIG.hotkeys.home.select_prev_account, "select_prev_account", "Select previous account"),
        (CONFIG.hotkeys.home.select_next_account, "select_next_account", "Select next account"),
    ]
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="home-page")
        self.isReady = get_accounts_count() and get_categories_count()
        accounts = get_all_accounts()
        self.mode = {
            "isIncome": False,
            "date": datetime.now(),
            "accountId": {
                "defaultValue": None,
                "defaultValueText": "Select account"
            }
        }
        if accounts:
            self.mode["accountId"]["defaultValue"] = accounts[0].id
            self.mode["accountId"]["defaultValueText"] = accounts[0].name
        self.accounts_indices = {
            "index": 0,
            "count": len(accounts)
        }
        self.accounts = accounts
        
    
    # -------------- Helpers ------------- #
    
    def rebuild(self) -> None:
        self.record_module.rebuild()
        self.insights_module.rebuild()
        self.accounts_module.rebuild()
        self.income_mode_module.rebuild()
        self.date_mode_module.rebuild()
    
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
    
    def action_toggle_income_mode(self) -> None:
        self.mode["isIncome"] = not self.mode["isIncome"]
        self.income_mode_module.rebuild()
        self.insights_module.rebuild()
    
    def _select_account(self, dir: int) -> None:
        new_index = (self.accounts_indices["index"] + dir) % self.accounts_indices["count"]
        self.accounts_indices["index"] = new_index
        self.mode["accountId"]["defaultValue"] = self.accounts[new_index].id
        self.mode["accountId"]["defaultValueText"] = self.accounts[new_index].name
        print(self.accounts[new_index].name)
        self.accounts_module.rebuild()

    def action_select_prev_account(self) -> None:
        self._select_account(-1)
    
    def action_select_next_account(self) -> None:
        self._select_account(1)
    
    #region View
    # --------------- View --------------- #
    
    def compose(self) -> ComposeResult:
        self.basePage = BasePage(
            pageName="Home",
            bindings =[]
        )
        with self.basePage:
            if not self.isReady:
                yield Label(
                    "Please create at least one account and one category to get started.",
                    classes="label-empty"
                )
            else:
                self.date_mode_module = DateMode(parent=self)
                self.income_mode_module = IncomeMode(parent=self)
                self.accounts_module = Accounts(parent=self)
                self.record_module = Records(parent=self)
                self.insights_module = Insights(parent=self)
                # with Container(classes=f"home-modules-container {self.app.layout}"):
                
                with Static(id="home-top-container"):
                    yield self.accounts_module
                    with Static(id="home-mode-container"):
                        yield self.income_mode_module
                        yield self.date_mode_module
                yield self.record_module
                yield self.insights_module
