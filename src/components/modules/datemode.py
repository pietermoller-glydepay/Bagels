from datetime import datetime, timedelta

from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Label, Static

from components.button import Button
from config import CONFIG


class DateMode(Static):
    def __init__(self, parent: Static, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="datemode-container", classes="module-container")
        super().__setattr__("border_title", "Period")
        super().__setattr__("border_subtitle", f"← {CONFIG.hotkeys.home.cycle_offset_type} →")
        self.page_parent = parent
        self.first_day_of_week = 6 # 0 = Monday, 6 = Sunday
    
    def on_mount(self) -> None:
        self.rebuild()
    
    #region Builder
    # -------------- Builder ------------- #
    def _get_calendar_days(self):
        """Returns list of (day_number, is_current) tuples for calendar"""
        filter_offset = self.page_parent.filter["offset"]
        filter_offset_type = self.page_parent.filter["offset_type"]
        
        if filter_offset_type != "year":
            # Calculate dates for the calendar
            today = datetime.now()
            
            if filter_offset_type == "month":
                current_date = datetime(today.year, today.month + filter_offset, 1)
            elif filter_offset_type == "week":
                current_date = today + timedelta(weeks=filter_offset)
                current_date = current_date.replace(day=1)
            else: # day
                current_date = today + timedelta(days=filter_offset)
                current_date = current_date.replace(day=1)
            
            # Get first day of month and number of days
            first_day = current_date.replace(day=1)
            if current_date.month == 12:
                next_month = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                next_month = current_date.replace(month=current_date.month + 1, day=1)
            days_in_month = (next_month - first_day).days
            
            # Get day of week for first day (adjusted for first_day_of_week)
            first_weekday = (first_day.weekday() - self.first_day_of_week) % 7
            
            days = []
            
            # Add days from previous month
            if first_weekday > 0:
                prev_month_days = first_day - timedelta(days=first_weekday)
                for _ in range(first_weekday):
                    days.append((str(prev_month_days.day), False))
                    prev_month_days += timedelta(days=1)
            
            # Add days of current month
            for day in range(1, days_in_month + 1):
                days.append((str(day), True))
            
            # Add days from next month to complete the grid
            remaining_days = (7 - len(days) % 7) % 7
            for day in range(1, remaining_days + 1):
                days.append((str(day), False))
                
            return days
        return []

    def rebuild(self) -> None:
        calendar_days = self._get_calendar_days()
        today = datetime.now()
        filter_offset = self.page_parent.filter["offset"]
        filter_offset_type = self.page_parent.filter["offset_type"]
        current_date = datetime(today.year, today.month + filter_offset, 1)
        
        # Update each calendar day label
        day_labels = self.query(".calendar-row Label")
        calendar_rows = self.query(".calendar-row")
        
        for row_idx, row in enumerate(calendar_rows):
            for col_idx, label in enumerate(row.query("Label")):
                list_idx = row_idx * 7 + col_idx
                if list_idx < len(calendar_days):
                    day, is_current = calendar_days[list_idx]
                    label.update(day)
                    
                    # Remove all special classes first
                    label.remove_class("not_current")
                    label.remove_class("today")
                    label.remove_class("this_month")
                    if col_idx == 0:
                        row.remove_class("this_week")
                    
                    # Add appropriate classes based on filter type
                    if not is_current:
                        label.add_class("not_current")
                    elif filter_offset_type == "month":
                        label.add_class("this_month")
                        if int(day) == today.day and current_date.month == today.month:
                            label.add_class("today")
                    elif filter_offset_type == "week":
                        first_day_of_week = today - timedelta(days=(today.weekday() - self.first_day_of_week) % 7) + timedelta(weeks=filter_offset)
                        if int(day) == first_day_of_week.day:
                            row.add_class("this_week")
                            if filter_offset != 0:
                                label.add_class("today")
                        if int(day) == today.day and current_date.month == today.month:
                            label.add_class("today")
                    elif filter_offset_type == "day":
                        if int(day) == today.day and current_date.month == today.month:
                            label.add_class("today")
        self.page_parent.update_filter_label(self.query_one(".current-filter-label"))

    # def on_button_pressed(self, event: Button.Pressed) -> None:
    #     if event.button.id == "prev-month":
    #         self.page_parent.action_prev_offset_type()
    #     elif event.button.id == "next-month":
    #         self.page_parent.action_next_offset_type()
    #     self.rebuild()
    
    #region View
    # --------------- View --------------- #

    def compose(self) -> ComposeResult:
        with Container(classes="month-selector"):
            yield Button("<<<", id="prev-month")
            yield Label("Current Month", classes="current-filter-label")
            yield Button(">>>", id="next-month")
            
        with Static(classes="calendar"):
            # Create 6 rows of 7 days each for the calendar grid
            for _ in range(6):
                with Horizontal(classes="calendar-row"):
                    for _ in range(7):
                        yield Label("", classes="not_current")