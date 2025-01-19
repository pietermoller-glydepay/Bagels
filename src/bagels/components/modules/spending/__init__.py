from datetime import datetime, timedelta

from textual.app import ComposeResult
from textual.binding import Binding
from textual.color import Color
from textual.containers import Horizontal
from textual.reactive import Reactive, reactive
from textual.widgets import Button, Label, Static

from bagels.components.indicators import EmptyIndicator
from bagels.components.modules.spending.plots import (
    BalancePlot,
    SpendingPlot,
    SpendingTrajectoryPlot,
)
from bagels.components.tplot import PlotextPlot
from bagels.components.tplot.plot import _rgbify
from bagels.config import CONFIG
from bagels.managers.utils import get_start_end_of_period
from bagels.utils.format import format_period_to_readable


class Spending(Static):
    PLOT_TYPES = [SpendingPlot, SpendingTrajectoryPlot, BalancePlot]

    can_focus = True
    offset: Reactive[int] = reactive(0)
    periods: Reactive[int] = reactive(1)
    current_plot: Reactive[int] = reactive(0)

    BINDINGS = [
        Binding("left", "dec_offset", "Shift back", show=True),
        Binding("right", "inc_offset", "Shfit front", show=True),
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            *args, **kwargs, id="spending-container", classes="module-container"
        )
        super().__setattr__("border_title", "Spending")
        self._plots = [plot_cls(self.app) for plot_cls in self.PLOT_TYPES]

    def on_mount(self) -> None:
        self.focus()
        self.rebuild()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "inc-offset":
            self.action_inc_offset()
        elif event.button.id == "dec-offset":
            self.action_dec_offset()
        elif event.button.id.startswith("plot-"):
            try:
                plot_index = int(event.button.id.split("-")[1])
                self.current_plot = plot_index
                self.query_one(".selected").set_classes("")
                event.button.set_classes("selected")
                self.rebuild()
            except ValueError:
                pass

    def rebuild(self) -> None:
        empty = self.query_one(EmptyIndicator)
        plotext = self.query_one(PlotextPlot)
        label = self.query_one(".current-view-label")
        plotext.display = False  # make plotext update by toggling display... for some reason. Maybe a bug? Who knows.
        plot = self._plots[self.current_plot]

        start_of_period, end_of_period = get_start_end_of_period(self.offset, "month")
        self.app.log(
            f"The plot type {plot.name} has support for cross periods: {plot.supports_cross_periods}"
        )
        self.app.log(
            f'Getting spending trend from "{start_of_period}" to "{end_of_period} ({self.offset} months ago)"'
        )
        label.update(
            format_period_to_readable({"offset": self.offset, "offset_type": "month"})
        )

        plt = self.query_one(PlotextPlot).plt
        plt.clear_data()
        plt.clear_figure()

        # ------------- get data ------------- #

        data = plot.get_data(start_of_period, end_of_period)
        total_days = (
            end_of_period - start_of_period
        ).days + 1  # add one to include the end date
        correct_data = len(data) == total_days
        empty.display = not correct_data
        plotext.display = correct_data
        if not correct_data:
            return

        # --------------- plot --------------- #

        dates = [
            (end_of_period - timedelta(days=i)).strftime("%d/%m/%Y")
            for i in range(total_days)
        ]

        plt.plot(
            dates,
            data,
            marker=CONFIG.defaults.plot_marker,
            color=_rgbify(Color.parse(self.app.themes[self.app.app_theme].accent).rgb),
        )

        # -------------- styling ------------- #

        plt.date_form(output_form="d")
        plt.xfrequency(total_days)

        line_color = _rgbify(Color.parse(self.app.themes[self.app.app_theme].panel).rgb)
        fdow_line_color = _rgbify(
            Color.parse(self.app.themes[self.app.app_theme].secondary).rgb
        )

        for d in dates:
            fdow = CONFIG.defaults.first_day_of_week
            d_datetime = datetime.strptime(d, "%d/%m/%Y")
            if d_datetime.weekday() == fdow:
                plt.vline(d, fdow_line_color)
            else:
                plt.vline(d, line_color)

        plt.xaxes(False)
        plt.yaxes(False)

        plot.plot(plt, start_of_period, end_of_period, self.offset, data)

    def action_inc_offset(self) -> None:
        if self.offset < 0:
            self.offset += 1
            self.rebuild()

    def action_dec_offset(self) -> None:
        self.offset -= 1
        self.rebuild()

    def compose(self) -> ComposeResult:
        with Horizontal(id="top-controls-container"):
            yield Button("<<<", id="dec-offset")
            yield Label("UPDATEME", classes="current-view-label")
            yield Button(">>>", id="inc-offset")
        yield PlotextPlot()
        yield EmptyIndicator("No data to display")
        with Horizontal(id="bottom-controls-container"):
            for i, plot in enumerate(self._plots):
                button_classes = "selected" if i == self.current_plot else ""
                yield Button(plot.name, id=f"plot-{i}", classes=button_classes)
