from abc import ABC, abstractmethod
from datetime import datetime

import numpy as np

from bagels.components.tplot.plot import Plot
from bagels.config import CONFIG
from bagels.managers.records import (
    get_daily_balance,
    get_net_income,
    get_spending,
    get_spending_trend,
)


class BasePlot(ABC):
    name: str = "Base Plot"
    supports_cross_periods: bool = False

    def __init__(self, app):
        self.app = app

    @abstractmethod
    def get_data(
        self, start_of_period: datetime, end_of_period: datetime
    ) -> list[float]:
        """Return a list of data points"""
        pass

    @abstractmethod
    def plot(
        self,
        plt: Plot,
        start_of_period: datetime,
        end_of_period: datetime,
        offset: int,
        data: list[float],
        dates: list[str],
        get_theme_color,
    ) -> None:
        """Additional operations on the plotext object."""
        pass


class SpendingPlot(BasePlot):
    name: str = "Spending"

    def get_data(self, start_of_period, end_of_period):
        return get_spending(start_of_period, end_of_period)

    def plot(
        self,
        plt: Plot,
        start_of_period: datetime,
        end_of_period: datetime,
        offset: int,
        data: list[float],
        dates: list[str],
        get_theme_color,
    ) -> None:
        if min(data) >= 0:
            plt.ylim(lower=0)


class SpendingTrajectoryPlot(BasePlot):
    name: str = "Spending Trajectory"

    def get_data(self, start_of_period, end_of_period):
        return get_spending_trend(start_of_period, end_of_period)

    def plot(
        self,
        plt: Plot,
        start_of_period: datetime,
        end_of_period: datetime,
        offset: int,
        data: list[float],
        dates: list[str],
        get_theme_color,
    ) -> None:
        # --------- Limit computation -------- #
        metric = CONFIG.state.budgeting.income_assess_metric  # use number if provided
        threshold = CONFIG.state.budgeting.income_assess_threshold
        fallback = CONFIG.state.budgeting.income_assess_fallback

        limit = 0
        if metric == "periodIncome":
            this_month_income = get_net_income(offset)
            if this_month_income > threshold:
                limit = this_month_income
            else:
                limit = get_net_income(offset - 1)

        if limit < fallback:
            limit = fallback

        print(f"Limit: {limit}")
        plt.ylim(upper=limit, lower=0)

        if len(data) == len(dates):
            return  # don't have to show regression prediction trend

        # ---------- Prediction line --------- #

        # Estimate data trend by creating an array of length len(dates) - len(data), filled with values from linear regression.
        # Plot the data by using reversed dates to put at the right hand side of the plot
        if len(data) >= 2:
            x = np.arange(len(data))
            coefficients = np.polyfit(x, data, 1)
            trend = np.poly1d(coefficients)

            # Generate prediction points for the remaining days
            remaining_days = len(dates) - len(data)
            if remaining_days > 0:
                prediction_x = np.arange(len(data), len(dates))
                prediction_y = trend(prediction_x)
                prediction_data = data + prediction_y.tolist()

                plt.plot(
                    dates,
                    prediction_data,
                    marker=CONFIG.defaults.plot_marker,
                    color=get_theme_color("secondary"),
                )

        # ----- Period spending separator ---- #

        period_spending = max(data)

        total_days = (end_of_period - start_of_period).days + 1

        plt.plot(
            dates,
            [period_spending] * total_days,
            marker=CONFIG.defaults.plot_marker,
            color=get_theme_color("panel"),
        )


class BalancePlot(BasePlot):
    name: str = "Balance"
    supports_cross_periods = True

    def get_data(self, start_of_period, end_of_period):
        return get_daily_balance(start_of_period, end_of_period)

    def plot(
        self,
        plt: Plot,
        start_of_period: datetime,
        end_of_period: datetime,
        offset: int,
        data: list[float],
        dates: list[str],
        get_theme_color,
    ) -> None:
        pass
