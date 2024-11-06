from pydantic import BaseModel
from rich.color import Color as RichColor
from rich.text import Text
from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Static

from config import CONFIG
from queries.categories import get_all_categories_records
from queries.utils import get_period_average, get_period_net


class PercentageBarItem(BaseModel):
    name: str
    count: int
    color: str

#region PercentageBar
class PercentageBar(Static):
    DEFAULT_CSS = """
    PercentageBar {
        layout: vertical;
        width: 1fr;
        height: auto;
    }
    
    PercentageBar > .bar {
        layout: horizontal;
        height: 3;
        
        .bar-item {
            padding: 1 0 1 0;
        }
    }
    
    PercentageBar > .labels {
        layout: vertical;
        height: auto;
        margin-top: 1;
        
        .bar-label {
            layout: horizontal;
            height: 1;
        }
        
        .bar-label > .percentage {
            margin-left: 2;
            color: $primary-background-lighten-3;
        }
    }
    
    """
    
    items: list[PercentageBarItem] = [
    ]
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def on_mount(self) -> None:
        self.rebuild()
    
    def set_items(self, items: list[PercentageBarItem]) -> None:
        self.items = items
        self.rebuild()
    
    def rebuild(self) -> None:
        # we first remove all existing items and labels
        for item in self.query(".bar-item"):
            item.remove()
        bar_labels = self.query(".bar-label")
        bar_labels_count = len(bar_labels)
        
        # we calculate the appropriate width for each item, with last item taking remaining space
        total = sum(item.count for item in self.items)
        bar = self.query_one(".bar")
        labels = self.query_one(".labels")
        
        for i, item in enumerate(self.items):
            item_widget = Static(" ", classes="bar-item")
            color = item.color
            percentage = round((item.count / total) * 100)
            if i + 1 > bar_labels_count: # if we have more items than labels, we create a new label
                label_widget = Container(
                    Label(f"[{color}]●[/{color}] {item.name}", classes="name"),
                    Label(f"{percentage}%", classes="percentage"),
                    classes="bar-label"
                )
                labels.mount(label_widget)
            else: 
                bar_label = bar_labels[i]
                bar_label.query_one(".name").update(f"[{color}]●[/{color}] {item.name}")
                bar_label.query_one(".percentage").update(f"{percentage}%")
            
            width = pwidth = f"{percentage}%"
            if i == len(self.items) - 1:
                # Last item takes remaining space
                width = "1fr"

            item_widget.styles.width = width
            item_widget.styles.background = Color.from_rich_color(RichColor.parse(item.color))
            item_widget.update(" " + pwidth)
                
            bar.mount(item_widget)
        
    def compose(self) -> ComposeResult:
        yield Container(classes="bar")
        yield Container(classes="labels")

#region PeriodBarchart
class PeriodBarchart(Static):
    pass

#region Insights
class Insights(Static):
    
    BINDINGS = [
        (CONFIG.hotkeys.home.insights.toggle_use_account, "toggle_use_account", "Toggle use account")
    ]
    
    can_focus = True
    
    def __init__(self, parent: Static, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="insights-container", classes="module-container")
        super().__setattr__("border_title", "Insights")
        self.page_parent = parent
        self.use_account = False # insights of specific account if True
    
    def on_mount(self) -> None:
        self.rebuild()
    
    #region Builder
    # -------------- Builder ------------- #
    
    def rebuild(self) -> None:
        items = self.get_percentage_bar_items()
        self.percentage_bar.set_items(items)
        
        current_filter_label = self.query_one(".current-filter-label")
        period_net_label = self.query_one(".period-net")
        period_average_label = self.query_one(".period-average")
        average_label = self.query_one(".average-label")
        
        mode_isIncome = self.page_parent.mode["isIncome"]
        label = "Income" if mode_isIncome else "Expense"
        
        current_filter_label.update(f"{label} of {self.page_parent.get_filter_label()}")
        average_label.update(f"{label} per day")
        if self.use_account:
            params = {
                **self.page_parent.filter,
                "accountId": self.page_parent.mode["accountId"]["defaultValue"],
                "isIncome": mode_isIncome
            }
        else:
            params = {
                **self.page_parent.filter,
                "isIncome": mode_isIncome
            }
        
        period_net = get_period_net(**params)
        period_average = get_period_average(period_net, **self.page_parent.filter)
        period_net_label.update(str(period_net))
        period_average_label.update(str(period_average))

    def get_percentage_bar_items(self, limit: int = 5) -> list[PercentageBarItem]:
        category_records = get_all_categories_records(**self.page_parent.filter, isExpense=not self.page_parent.mode["isIncome"])
        
        # Sort categories by percentage in descending order
        items = []
        if len(category_records) <= limit:
            # If we have 5 or fewer categories, show them all
            for category in category_records:
                items.append(PercentageBarItem(
                    name=category.name,
                    count=category.percentage,
                    color=category.color
                ))
        else:
            # Show top 4 categories and group the rest as "Others"
            for category in category_records[:limit]:
                items.append(PercentageBarItem(
                    name=category.name,
                    count=category.percentage,
                    color=category.color
                ))
                
            # Sum up the percentages of remaining categories
            others_percentage = sum(cat.percentage for cat in category_records[limit:])
            items.append(PercentageBarItem(
                name="Others",
                count=others_percentage,
                color="white"
            ))
        
        return items

    def get_period_barchart_items(self) -> list[PercentageBarItem]:
        items = []
        return items

    #region Callbacks
    # ------------- callbacks ------------ #
    def action_toggle_use_account(self) -> None:
        self.use_account = not self.use_account
        self.rebuild()
        
    #region View
    # --------------- View --------------- #

    def compose(self) -> ComposeResult:
        with Horizontal(classes="figures-container"):
            with Container(classes="net container"):
                yield Label(classes="current-filter-label title") # dynamic
                yield Label("Loading...", classes="period-net amount") # dynamic
            with Container(classes="average container"):
                yield Label("<> per day", classes="average-label title") # dynamic
                yield Label("Loading...", classes="period-average amount") # dynamic
            
        self.percentage_bar = PercentageBar()
        self.period_barchart = PeriodBarchart()
        yield self.percentage_bar
        yield self.period_barchart
