from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Input, Label, Static

from bagels.config import CONFIG, write_state
from bagels.managers.utils import (
    dynamic_cache,
    get_income_to_use,
    get_period_figures,
    try_method_query_one,
)
from bagels.models.category import Nature


class Budgets(Static):
    can_focus = True

    def __init__(self, page_parent, *args, **kwargs) -> None:
        super().__init__(
            *args, **kwargs, id="budgets-container", classes="module-container"
        )
        super().__setattr__("border_title", "Budgeting")
        self.page_parent = page_parent

    # --------------- Hooks -------------- #

    def on_mount(self) -> None:
        self.rebuild()

    def _write_state(self, key: str, value: float) -> bool:
        current_value = CONFIG.state
        for part in key.split("."):
            current_value = getattr(current_value, part)
        if value and current_value != value:
            write_state(key, value)
            return True
        return False

    def on_input_changed(self, event: Input.Changed) -> None:
        updated = False
        if event.input.id == "savings-input":
            if self.savings_assess_metric.startswith("percentage"):
                updated = self._write_state(
                    "budgeting.savings_percentage", float(event.value)
                )
            else:
                updated = self._write_state(
                    "budgeting.savings_amount", float(event.value)
                )

        elif event.input.id == "wants-input":
            if self.wants_spending_assess_metric.startswith("percentage"):
                updated = self._write_state(
                    "budgeting.wants_spending_percentage", float(event.value)
                )
            else:
                updated = self._write_state(
                    "budgeting.wants_spending_amount", float(event.value)
                )
        if updated:
            self.rebuild()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id.startswith("savings-"):
            metric = event.button.id.replace("savings-", "")
            self._write_state("budgeting.savings_assess_metric", metric)
        elif event.button.id.startswith("wants-"):
            metric = event.button.id.replace("wants-", "")
            self._write_state("budgeting.wants_spending_assess_metric", metric)
        self.rebuild()

    # region Builders
    # ------------- Builders ------------- #

    def rebuild(self) -> None:
        self.savings_assess_metric = CONFIG.state.budgeting.savings_assess_metric
        try_method_query_one(self, "#savings-row > .selected", "set_classes", [""])
        try_method_query_one(
            self, f"#savings-{self.savings_assess_metric}", "set_classes", ["selected"]
        )
        restrict_percentage = r"0\.([0-9]){0,2}"
        restrict_amount = r"\d*\.?\d{0,2}"
        input = self.query_one("#savings-input")
        if self.savings_assess_metric.startswith("percentage"):
            input.value = str(CONFIG.state.budgeting.savings_percentage)
            input.restrict = restrict_percentage
        else:
            input.value = str(CONFIG.state.budgeting.savings_amount)
            input.restrict = restrict_amount

        self.wants_spending_assess_metric = (
            CONFIG.state.budgeting.wants_spending_assess_metric
        )
        input = self.query_one("#wants-input")
        try_method_query_one(self, "#wants-row > .selected", "set_classes", [""])
        try_method_query_one(
            self,
            f"#wants-{self.wants_spending_assess_metric}",
            "set_classes",
            ["selected"],
        )
        if self.wants_spending_assess_metric.startswith("percentage"):
            input.value = str(CONFIG.state.budgeting.wants_spending_percentage)
            input.restrict = restrict_percentage
        else:
            input.value = str(CONFIG.state.budgeting.wants_spending_amount)
            input.restrict = restrict_amount
        self._rebuild_income_bar()

    def _rebuild_income_bar(self) -> None:
        offset = self.page_parent.offset
        net_income = dynamic_cache(get_income_to_use, offset)
        net_expenses = dynamic_cache(
            get_period_figures, isIncome=False, offset=offset, offset_type="month"
        )
        amount_to_save = round(
            net_income * CONFIG.state.budgeting.savings_percentage
            if self.savings_assess_metric.startswith("percentage")
            else CONFIG.state.budgeting.savings_amount,
            CONFIG.defaults.round_decimals,
        )
        expenses_must = dynamic_cache(
            get_period_figures,
            isIncome=False,
            offset=offset,
            offset_type="month",
            nature=Nature.MUST,
        )
        expenses_need = dynamic_cache(
            get_period_figures,
            isIncome=False,
            offset=offset,
            offset_type="month",
            nature=Nature.NEED,
        )
        expenses_want = net_expenses - expenses_must - expenses_need

        self.app.log(
            f"Data: net_income={net_income}, net_expenses={net_expenses}, amount_to_save={amount_to_save}, expenses_must={expenses_must}, expenses_need={expenses_need}, expenses_want={expenses_want}"
        )

        income_bar_container = self.query_one("#income-bar")
        empty_bar = self.query_one(".empty-bar")

        income_bar_container.display = not not net_income
        empty_bar.display = not net_income

        if not net_income:
            return

        row1 = income_bar_container.query_one("#row-1")
        p_expenses = round(net_expenses / net_income * 100)
        p_saving = round(amount_to_save / net_income * 100)
        row1_columns = f"{p_expenses}% {p_saving}% 1fr"
        self.app.log(row1_columns)
        row1.styles.grid_columns = row1_columns

        row2 = income_bar_container.query_one("#row-2")
        row2.styles.grid_columns = f"{p_expenses}%  1fr"

        label_spent_amount = income_bar_container.query_one("#label-spent-amount")
        label_spent_amount.update(str(net_expenses))
        label_save_amount = income_bar_container.query_one("#label-save-amount")
        label_save_amount.update(str(amount_to_save))
        label_remaining_amount = income_bar_container.query_one(
            "#label-remaining-amount"
        )
        remaining = round(
            net_income - net_expenses - amount_to_save, CONFIG.defaults.round_decimals
        )
        label_remaining_amount.update(str(remaining))

        row3 = income_bar_container.query_one("#row-3")
        row3.display = not not net_expenses  # only display if there are expenses
        income_bar_container.styles.height = 5 if not not net_expenses else 4

        if not not net_expenses:
            p_must = round(expenses_must / net_expenses * 100)
            p_need = round(expenses_need / net_expenses * 100)
            row3_columns = f"{p_must}% {p_need}% 1fr"
            self.app.log(row3_columns)
            row3.styles.grid_columns = row3_columns
            row3.styles.width = f"{p_expenses}%"

    # region View
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        with Horizontal(id="savings-row", classes="config-rows"):
            yield Label("Savings: ", id="savings-label")
            yield Button(
                "% Period Income",
                tooltip="percentagePeriodIncome",
                id="savings-percentagePeriodIncome",
            )
            yield Button("Set amount", tooltip="setAmount", id="savings-setAmount")
            yield Input(placeholder="0.0", id="savings-input")
        with Horizontal(id="wants-row", classes="config-rows"):
            yield Label("Wants: ", id="wants-label")
            yield Button("% Expenses", tooltip="percentage", id="wants-percentage")
            yield Button("Set amount", tooltip="setAmount", id="wants-setAmount")
            yield Input(
                placeholder="0.0",
                id="wants-input",
            )
        with Container(id="income-bar"):
            with Container(id="row-0"):
                with Horizontal():
                    yield Label("╭ Spent: ")
                    yield Label("0.0", id="label-spent-amount")
                with Horizontal(id="remaining"):
                    yield Label("Remaining: ")
                    yield Label("0.0", id="label-remaining-amount")
                    yield Label(" ╮")
            with Container(id="row-1"):
                yield Static(id="bar-spent")
                yield Static(id="bar-saving")
                yield Static(id="bar-remaining")
            with Container(id="row-2"):
                yield Static()
                with Horizontal():
                    yield Label("╰ Save: ")
                    yield Label("0.0", id="label-save-amount")
            with Container(id="row-3"):
                yield Static(id="bar-spent-must")
                yield Static(id="bar-spent-need")
                yield Static(id="bar-spent-want")
                yield Label("Must")
                yield Label("Need")
                yield Label("Want")
        with Container(classes="empty-bar"):
            yield Label("Nothing to display. Budgeting depends on your income!")
