from pydantic import BaseModel
from rich.color import Color as RichColor
from rich.text import Text
from textual.app import ComposeResult
from textual.color import Color
from textual.containers import Container
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
        height: 1;
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
        self._update()
    
    def set_items(self, items: list[PercentageBarItem]) -> None:
        self.items = items
        self._update()
    
    def _update(self) -> None:
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
            item_widget.update(pwidth)
                
            bar.mount(item_widget)
            labels.mount(label_widget)
        
    def compose(self) -> ComposeResult:
        yield Container(classes="bar")
        yield Container(classes="labels")
        
def get_percentage_bar_items(limit: int = 5) -> list[PercentageBarItem]:
    category_records = get_all_categories_records()
    
    # Sort categories by percentage in descending order
    sorted_categories = sorted(category_records, key=lambda x: x.percentage, reverse=True)
    
    items = []
    if len(sorted_categories) <= limit:
        # If we have 5 or fewer categories, show them all
        for category in sorted_categories:
            items.append(PercentageBarItem(
                name=category.name,
                count=category.percentage,
                color=category.color
            ))
    else:
        # Show top 4 categories and group the rest as "Others"
        for category in sorted_categories[:limit]:
            items.append(PercentageBarItem(
                name=category.name,
                count=category.percentage,
                color=category.color
            ))
            
        # Sum up the percentages of remaining categories
        others_percentage = sum(cat.percentage for cat in sorted_categories[limit:])
        items.append(PercentageBarItem(
            name="Others",
            count=others_percentage,
            color="white"
        ))
    
    return items
    
#region Insights
class Insights(Static):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def on_mount(self) -> None:
        self._update_insights()
    
    #region Builder
    # -------------- Builder ------------- #
    
    def _update_insights(self) -> None:
        items = get_percentage_bar_items()
        self.percentage_bar.set_items(items)
        
    #region View
    # --------------- View --------------- #

    def compose(self) -> ComposeResult:
        insightsContainer = Container(id="insights-container", classes="module-container")
        insightsContainer.border_subtitle = "Insights"
        with insightsContainer:
            self.percentage_bar = PercentageBar()
            yield self.percentage_bar
