from datetime import datetime, timedelta

from textual.app import ComposeResult
from textual.binding import Binding
from textual.color import Color
from textual.containers import Horizontal
from textual.reactive import Reactive, reactive
from textual.widgets import Button, Label, Static

from bagels.components.indicators import EmptyIndicator
from bagels.components.tplot import PlotextPlot
from bagels.components.tplot.plot import _rgbify
from bagels.config import CONFIG
from bagels.managers.records import get_spending_trend
from bagels.managers.utils import get_start_end_of_period


class Spending(Static):
    can_focus = True

    number_of_weeks: Reactive[int] = reactive(2)
    view_offset: Reactive[int] = reactive(0)

    BINDINGS = [
        Binding("left", "dec_offset", "Shift back", show=True),
        Binding("right", "inc_offset", "Shfit front", show=True),
        Binding("-", "inc_weekcount", "Zoom out", show=True),
        Binding("+", "dec_weekcount", "Zoom in", show=True),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args, **kwargs, id="spending-container", classes="module-container"
        )
        super().__setattr__("border_title", "Spending")

    # --------------- Hooks -------------- #

    def on_mount(self) -> None:
        self.focus()
        self.rebuild()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "inc-offset":
            self.action_inc_offset()
        elif event.button.id == "dec-offset":
            self.action_dec_offset()
        elif event.button.id == "inc-weekcount":
            self.action_inc_weekcount()
        elif event.button.id == "dec-weekcount":
            self.action_dec_weekcount()

    # region Builders
    # ------------- Builders ------------- #

    def rebuild(self) -> None:
        empty = self.query_one(EmptyIndicator)
        plotext = self.query_one(PlotextPlot)
        label = self.query_one(".current-view-label")
        plotext.display = False

        start_of_period, end_of_period = get_start_end_of_period(
            self.view_offset, "week"
        )
        start_of_period = start_of_period - timedelta(weeks=self.number_of_weeks - 1)
        self.app.log(
            f'Getting spending trend from "{start_of_period}" to "{end_of_period} ({self.number_of_weeks} weeks, {self.view_offset} weeks ago)"'
        )
        label.update(
            f"Period {start_of_period.strftime('%d/%m/%Y')} -> {end_of_period.strftime('%d/%m/%Y')} ({self.number_of_weeks} weeks, {-self.view_offset} weeks ago)"
        )
        spending = get_spending_trend(start_of_period, end_of_period)
        if len(spending) == 0:
            empty.display = True
            return
        else:
            empty.display = False
            plotext.display = True

        plt = self.query_one(PlotextPlot).plt

        dates = [
            (end_of_period - timedelta(days=i)).strftime("%d/%m/%Y")
            for i in range(len(spending))
        ]

        self.app.log(f"Dates: {dates}")
        self.app.log(f"Spending: {spending}")
        self.app.log(self.app.themes[self.app.app_theme].accent)
        plt.clear_data()
        plt.clear_figure()
        plt.plot(
            dates,
            spending,
            marker="braille",
            color=_rgbify(Color.parse(self.app.themes[self.app.app_theme].accent).rgb),
        )
        plt.date_form(output_form="d")
        plt.xfrequency(len(dates))
        line_color = _rgbify(Color.parse(self.app.themes[self.app.app_theme].panel).rgb)
        fdow_line_color = _rgbify(
            Color.parse(self.app.themes[self.app.app_theme].secondary).rgb
        )
        for d in dates:
            fdow = CONFIG.defaults.first_day_of_week  # 6 is sunday
            d_datetime = datetime.strptime(d, "%d/%m/%Y")
            if d_datetime.weekday() == fdow:
                plt.vline(d, fdow_line_color)
            else:
                plt.vline(d, line_color)
        plt.xaxes(False)
        plt.yaxes(False)

    # region Callbacks
    # ------------- Callbacks ------------ #

    def action_inc_offset(self) -> None:
        if self.view_offset < 0:
            self.view_offset += 1
            self.rebuild()

    def action_dec_offset(self) -> None:
        self.view_offset -= 1
        self.rebuild()

    def action_inc_weekcount(self) -> None:
        if self.number_of_weeks < 12:
            self.number_of_weeks += 1
            self.rebuild()

    def action_dec_weekcount(self) -> None:
        if self.number_of_weeks > 1:
            self.number_of_weeks -= 1
            self.rebuild()

    # region View
    # --------------- View --------------- #
    def compose(self) -> ComposeResult:
        with Horizontal(id="top-controls-container"):
            yield Button("+", id="dec-weekcount")  # zoom in
            yield Button("<<<", id="dec-offset")
            yield Label("UPDATEME", classes="current-view-label")
            yield Button(">>>", id="inc-offset")
            yield Button("-", id="inc-weekcount")  # zoom out
        yield PlotextPlot()
        yield EmptyIndicator("No data to display")
