from pydantic import BaseModel
from rich.color import Color as RichColor
from rich.text import Text
from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Label, Static

from controllers.categories import get_all_categories_records


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
        height: auto;
        
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
        for label in self.query(".bar-label"):
            label.remove()
        
        # we calculate the appropriate width for each item, with last item taking remaining space
        total = sum(item.count for item in self.items)
        bar = self.query_one(".bar")
        labels = self.query_one(".labels")
        
        for i, item in enumerate(self.items):
            item_widget = Static(" ", classes="bar-item")
            color = item.color
            percentage = round((item.count / total) * 100)
            label_widget = Container(
                Label(f"[{color}]●[/{color}] {item.name}", classes="name"),
                Label(f"{percentage}%", classes="percentage"),
                classes="bar-label"
            )
            
            width = pwidth = f"{percentage}%"
            if i == len(self.items) - 1:
                # Last item takes remaining space
                width = "1fr"

            item_widget.styles.width = width
            item_widget.styles.background = Color.from_rich_color(RichColor.parse(item.color))
            item_widget.update(" " + pwidth)
                
            bar.mount(item_widget)
            labels.mount(label_widget)
        
    def compose(self) -> ComposeResult:
        yield Container(classes="bar")
        yield Container(classes="labels")

#region PeriodBarchart
class PeriodBarchart(Static):
    pass

#region Insights
class Insights(Static):
    can_focus = True
    
    def __init__(self, parent: Static, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="insights-container", classes="module-container")
        self.page_parent = parent
    
    def on_mount(self) -> None:
        self.rebuild()
    
    #region Builder
    # -------------- Builder ------------- #
    
    def rebuild(self) -> None:
        items = self.get_percentage_bar_items()
        self.percentage_bar.set_items(items)
        self.page_parent.update_filter_label(self.query_one(".current-filter-label"))

    def get_percentage_bar_items(self, limit: int = 5) -> list[PercentageBarItem]:
        category_records = get_all_categories_records(**self.page_parent.filter)
        
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
        
    #region View
    # --------------- View --------------- #

    def compose(self) -> ComposeResult:
        with Horizontal(classes="figures-container"):
            with Container(classes="net container"):
                yield Label(classes="current-filter-label title")
                yield Label("$0.00", classes="period-net amount")
            with Container(classes="average container"):
                yield Label("Expense per day", classes="title")
                yield Label("$0.00", classes="period-average amount")
            
        self.percentage_bar = PercentageBar()
        self.period_barchart = PeriodBarchart()
        yield self.percentage_bar
        yield self.period_barchart
