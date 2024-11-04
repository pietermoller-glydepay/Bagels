from textual.app import ComposeResult
from textual.widgets import Label, Static, Switch


class IncomeMode(Static):
    can_focus = True
    
    def __init__(self, parent: Static, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="incomemode-container", classes="module-container")
        super().__setattr__("border_title", "View and add")
        self.page_parent = parent
    
    def on_mount(self) -> None:
        self.rebuild()
    
    #region Builder
    # -------------- Builder ------------- #
    
    def rebuild(self) -> None:
        expense_label: Label = self.query_one("#expense-label")
        income_label: Label = self.query_one("#income-label")
        current_is_income = self.page_parent.mode["isIncome"]
        expense_label.classes = "selected" if not current_is_income else ""
        income_label.classes = "selected" if current_is_income else ""
    
    #region View
    # --------------- View --------------- #

    def compose(self) -> ComposeResult:
        yield Label("Expense", id="expense-label")
        yield Label("Income", id="income-label")
