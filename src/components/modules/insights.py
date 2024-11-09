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
    
    PercentageBar > .bar-container {
        layout: horizontal;
        height: 1;
        width: 1fr;
        
        .bar {
            layout: horizontal;
            height: 1;
            width: 1fr;
            
            .empty-bar {
                hatch: right $panel-lighten-2;
                
                Label {
                    dock: left;
                    align-horizontal: center;
                    padding: 0 1 0 1;
                }
            }
            
            # .bar-item {
            #     padding: 1 0 1 0;
            # }
        }
    }
    
    
    PercentageBar > .labels-container {
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
        self.rounded = True
    
    def on_mount(self) -> None:
        self.rebuild()
    
    def set_items(self, items: list[PercentageBarItem]) -> None:
        self.items = items
        self.rebuild()
    
    #  50%  50% 
    # ^-----======^
    def rebuild(self) -> None:
        # we first remove all existing items and labels
        for item in self.query(".bar-item"):
            item.remove()
        labels = self.query(".bar-label")
        labels_count = len(labels)
        items_count = len(self.items)
        
        prev_empty_bar = self.bar.query(".empty-bar")
        if len(self.items) == 0:
            if self.rounded:
                self.bar_start.styles.display = "none"
                self.bar_end.styles.display = "none"
            if len(prev_empty_bar) == 0:
                empty_bar = Container(Label("No data to display"), classes="empty-bar")
                self.bar.mount(empty_bar)
        else:
            if self.rounded:
                self.bar_start.styles.display = "block"
                self.bar_end.styles.display = "block"
            if len(prev_empty_bar) > 0:
                prev_empty_bar[0].remove()
        
        to_remove_count = labels_count - items_count
        if to_remove_count > 0:
            for i in range(to_remove_count):
                labels[i + items_count].remove()
        # we calculate the appropriate width for each item, with last item taking remaining space
        total = sum(item.count for item in self.items)
        for i, item in enumerate(self.items):
            item_widget = Static(" ", classes="bar-item")
            color = item.color
            background_color = Color.from_rich_color(RichColor.parse(item.color)).hex
            # assign start and end colors
            if self.rounded:
                if i == 0:
                    self.bar_start.styles.color = background_color
                if i == len(self.items) - 1:
                    self.bar_end.styles.color = background_color
            # calculate percentage
            percentage = round((item.count / total) * 100)
            if i + 1 > labels_count: # if we have more items than labels, we create a new label
                label_widget = Container(
                    Label(f"[{color}]●[/{color}] {item.name}", classes="name"),
                    Label(f"{percentage}%", classes="percentage"),
                    classes="bar-label"
                )
                self.labels_container.mount(label_widget)
            else: 
                label = labels[i]
                label.query_one(".name").update(f"[{color}]●[/{color}] {item.name}")
                label.query_one(".percentage").update(f"{percentage}%")
            
                
            width = f"{percentage}%"
            if i == len(self.items) - 1:
                # Last item takes remaining space
                width = "1fr"

            item_widget.styles.width = width
            item_widget.styles.background = background_color
            if self.rounded:
                if i > 0:
                    prev_background_color = Color.from_rich_color(RichColor.parse(self.items[i - 1].color)).hex
                    item_widget.update(f"[{prev_background_color} on {background_color}][/{prev_background_color} on {background_color}]")
                
                
            self.bar.mount(item_widget)
        
    def compose(self) -> ComposeResult:
        self.bar_start = Label("", classes="bar-start")
        self.bar = Container(classes="bar")
        self.bar_end = Label("", classes="bar-end")
        self.labels_container = Container(classes="labels-container")
        with Container(classes="bar-container"):
            if self.rounded: yield self.bar_start
            yield self.bar
            if self.rounded: yield self.bar_end
        yield self.labels_container

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
        # super().__setattr__("border_subtitle", CONFIG.hotkeys.home.insights.toggle_use_account)
        self.page_parent = parent
        self.use_account = False # insights of specific account if True
    
    def on_mount(self) -> None:
        self.rebuild()
    
    #region Builder
    # -------------- Builder ------------- #

    def rebuild(self) -> None:
        items = self.get_percentage_bar_items()
        self.percentage_bar.set_items(items)
        self._update_labels()
    
    def _update_labels(self) -> None:
        current_filter_label = self.query_one(".current-filter-label")
        period_net_label = self.query_one(".period-net")
        period_average_label = self.query_one(".period-average")
        average_label = self.query_one(".average-label")
        
        mode_isIncome = self.page_parent.mode["isIncome"]
        label = "Income" if mode_isIncome else "Expense"
        
        if self.use_account:
            current_filter_label.update(f"{self.page_parent.mode['accountId']['defaultValueText']} {label} of {self.page_parent.get_filter_label()}")
        else:
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
        if self.use_account:
            category_records = get_all_categories_records(
                **self.page_parent.filter,
                isExpense=not self.page_parent.mode["isIncome"],
                account_id=self.page_parent.mode["accountId"]["defaultValue"]
            )
        else:
            category_records = get_all_categories_records(
                **self.page_parent.filter,
                isExpense=not self.page_parent.mode["isIncome"]
            )
        
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
