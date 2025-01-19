from abc import ABC, abstractmethod
from datetime import datetime

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
    ) -> None:
        plt.ylim(lower=0)
        pass


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
    ) -> None:
        # here we compare our cumulative spending to our income.
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

        period_spending = max(data)
        print(period_spending)


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
    ) -> None:
        pass
