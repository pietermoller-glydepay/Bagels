from datetime import datetime, timedelta

from textual.app import ComposeResult
from textual.widgets import Static
from textual_plotext import PlotextPlot

from bagels.managers.records import get_spending_trend


class Spending(Static):
    can_focus = True

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args, **kwargs, id="spending-container", classes="module-container"
        )
        super().__setattr__("border_title", "Spending")

    # --------------- Hooks -------------- #

    def on_mount(self) -> None:
        self.rebuild()

    # region Builders
    # ------------- Builders ------------- #

    def rebuild(self) -> None:
        plt = self.query_one(PlotextPlot).plt
        number_of_weeks = 5
        view_offset = 2
        spending = get_spending_trend(number_of_weeks, view_offset)
        end_of_period = datetime.now() - timedelta(weeks=number_of_weeks)
        dates = [
            (end_of_period + timedelta(days=i)).strftime("%d/%m/%Y")
            for i in range(len(spending))
        ]
        plt.plot(dates, spending)
        plt.title("Spending trend")
        plt.xlabel("Days")
        plt.ylabel("Amount")

    # region View
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        yield PlotextPlot()
