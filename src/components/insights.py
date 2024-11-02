from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import Label, Static

from controllers.records import get_top_categories


class PercentageBarItem:
    name: str
    count: int
    color: str

#region PercentageBar
class PercentageBar(Static):
    DEFAULT_CSS = """
    PercentageBar {
        layout: vertical;
        width: 1fr;
        height: 2;
    }
    
    PercentageBar > .bar {
        layout: horizontal;
    }
    
    PercentageBar > .labels {
        layout: horizontal;
    }
    """
    
    items: list[PercentageBarItem] = []
    
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def on_mount(self) -> None:
        self._update()
    
    def set_items(self, items: list[PercentageBarItem]) -> None:
        self.items = items
        self._update()
    
    def _update(self) -> None:
        # we calculate the appropriate width for each item, with last item taking remaining space
        total = sum(item['count'] for item in self.items)
        bar = self.query_one(".bar")
        labels = self.query_one(".labels")
        
        for i, item in enumerate(self.items):
            item_widget = Static(" ", classes="bar-item")
            label_widget = Static(item['name'], classes="bar-label")
            item_widget.styles.background = item['color']
            width = pwidth =  f"{round((item['count'] / total) * 100)}%"
            
            if i == len(self.items) - 1:
                # Last item takes remaining space
                width = "1fr"
            item_widget.styles.width = width
            item_widget.update(pwidth)
            label_widget.styles.width = width
                
            bar.mount(item_widget)
            labels.mount(label_widget)
        
    def compose(self) -> ComposeResult:
        yield Container(classes="bar")
        yield Container(classes="labels")
        
# def get_category_percentage_by_month(month_offset: int = 0) -> list[CategoryPercentage]:
#     top_categories = get_top_categories(month_offset)
#     pass
    
#region Insights
class Insights(Static):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
    def on_mount(self) -> None:
        self._update_insights()
    
    #region Builder
    # -------------- Builder ------------- #
    
    def _update_insights(self) -> None:
        # get all expenses in the current month, and 
        pass
        
    #region View
    # --------------- View --------------- #

    def compose(self) -> ComposeResult:
        insightsContainer = Container(id="insights-container", classes="module-container")
        insightsContainer.border_subtitle = "Insights"
        with insightsContainer:
            self.percentage_bar = PercentageBar()
            yield self.percentage_bar
