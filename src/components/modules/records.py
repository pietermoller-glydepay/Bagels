from datetime import datetime, timedelta

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Label, Static

from components.button import Button
from components.datatable import DataTable
from components.indicators import EmptyIndicator
from components.modals import ConfirmationModal, RecordModal, TransferModal
from config import CONFIG
from controllers.accounts import (get_accounts_count,
                                  get_all_accounts_with_balance)
from controllers.persons import get_persons_with_splits
from controllers.records import (create_record, create_record_and_splits,
                                 delete_record, get_record_by_id,
                                 get_record_total_split_amount, get_records,
                                 update_record_and_splits)
from utils.format import format_date_to_readable
from utils.forms import RecordForm


class DisplayMode():
    DATE = "d"
    PERSON = "p"

class Records(Static):
    BINDINGS = [
        (CONFIG.hotkeys.new, "new_record", "Add"),
        (CONFIG.hotkeys.delete, "delete_record", "Delete"),
        (CONFIG.hotkeys.edit, "edit_record", "Edit"),
        (CONFIG.hotkeys.home.new_transfer, "new_transfer", "Transfer"),
        (CONFIG.hotkeys.home.toggle_splits, "toggle_splits", "Toggle Splits"),
        (CONFIG.hotkeys.home.display_by_person, "display_by_person", "Display by Person"),
        (CONFIG.hotkeys.home.display_by_date, "display_by_date", "Display by Date"),
    ]
    
    can_focus = True
    show_splits = True
    displayMode = reactive(DisplayMode.DATE)
    
    def __init__(self, parent: Static, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="records-container", classes="module-container")
        # super().border_subtitle="Records"
        self.page_parent = parent
        self.record_form = RecordForm()
    
    def on_mount(self) -> None:
        self.rebuild()
    
    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        current_row_index = event.cursor_row
        if event.row_key and event.row_key.value:
            self.current_row = event.row_key.value
        else:
            self.table.move_cursor(row=current_row_index + 1)
            
    
    # ---------- Table builders ---------- #
    #region Table
        
    def rebuild(self) -> None:
        table = self.table
        empty_indicator: EmptyIndicator = self.query_one("#empty-indicator")
        self._initialize_table(table)
        records = get_records(**self.page_parent.filter)
        
        if records or self.displayMode == DisplayMode.PERSON:
            match self.displayMode:
                case DisplayMode.PERSON:
                    self._build_person_view(table, records)
                case DisplayMode.DATE:
                    self._build_date_view(table, records)
                case _:
                    pass
        else:
            self.current_row = None
            
        table.focus()
        empty_indicator.display = not table.rows

    def _initialize_table(self, table: DataTable) -> None:
        table.clear()
        table.columns.clear()
        match self.displayMode:
            case DisplayMode.PERSON:
                table.add_columns(" ", "Date", "Record date", "Category", "Amount", "Paid to account")
            case DisplayMode.DATE:
                table.add_columns(" ", "Category", "Amount", "Label", "Account")

    def _build_date_view(self, table: DataTable, records: list) -> None:
        prev_group = None
        for record in records:
            flow_icon = self._get_flow_icon(len(record.splits) > 0, record.isIncome)
            
            category_string, amount_string = self._format_category_and_amount(record, flow_icon)
            label_string = record.label if record.label else "-"
            
            # Add group header based on filter type
            group_string = None
            match self.page_parent.filter["offset_type"]:
                case "year":
                    # Group by month
                    group_string = record.date.strftime("%B %Y")
                case "month": 
                    # Group by week
                    week_start = record.date - timedelta(days=record.date.weekday())
                    week_end = week_start + timedelta(days=6)
                    group_string = f"{format_date_to_readable(week_start)} - {format_date_to_readable(week_end)}"
                case "week":
                    # Group by day
                    group_string = format_date_to_readable(record.date)
                case "day":
                    # No grouping
                    pass
                    
            if group_string and prev_group != group_string:
                prev_group = group_string
                self._add_group_header_row(table, group_string)
            
            # Add main record row
            table.add_row(
                " ",
                category_string,
                amount_string,
                label_string,
                record.account.name,
                key=str(record.id),
            )
            
            # Add split rows if applicable
            if record.splits and self.show_splits:
                self._add_split_rows(table, record, flow_icon)

    def _get_flow_icon(self, recordHasSplits: bool, is_income: bool) -> str:
        if recordHasSplits and not self.show_splits:
            flow_icon_positive = f"[green]=[/green]"
            flow_icon_negative = f"[red]=[/red]"
        else:
            flow_icon_positive = f"[green]{CONFIG.symbols.amount_positive}[/green]"
            flow_icon_negative = f"[red]{CONFIG.symbols.amount_negative}[/red]"
        return flow_icon_positive if is_income else flow_icon_negative

    def _format_category_and_amount(self, record, flow_icon: str) -> tuple[str, str]:
        if record.isTransfer:
            category_string = f"{record.account.name} → {record.transferToAccount.name}"
            amount_string = record.amount
        else:
            color_tag = record.category.color.lower()
            category_string = f"[{color_tag}]{CONFIG.symbols.category_color}[/{color_tag}] {record.category.name}"
            
            if record.splits and not self.show_splits:
                amount_self = record.amount - get_record_total_split_amount(record.id)
                amount_string = f"{flow_icon} {amount_self}"
            else:
                amount_string = f"{flow_icon} {record.amount}"
                
        return category_string, amount_string

    def _add_group_header_row(self, table: DataTable, string: str) -> None:
        table.add_row(
            ">",
            string,
            "",
            "",
            "",
            style_name="group-header"
        )

    def _add_split_rows(self, table: DataTable, record, flow_icon: str) -> None:
        color = record.category.color.lower()
        amount_self = record.amount - get_record_total_split_amount(record.id)
        split_flow_icon = f"[red]{CONFIG.symbols.amount_negative}[/red]" if record.isIncome else f"[green]{CONFIG.symbols.amount_positive}[/green]"
        line_char = f"[{color}]{CONFIG.symbols.line_char}[/{color}]"
        finish_line_char = f"[{color}]{CONFIG.symbols.finish_line_char}[/{color}]"
        
        for split in record.splits:
            paid_status_icon = self._get_split_status_icon(split)
            date_string = Text(f"Paid on: {format_date_to_readable(split.paidDate)}", style="italic") if split.paidDate else Text("-")
            
            table.add_row(
                " ",
                f"{line_char} {paid_status_icon} {split.person.name}",
                f"{split_flow_icon} {split.amount}",
                date_string,
                split.account.name if split.account else "-"
            )
            
        # Add net amount row
        table.add_row(
            "",
            f"{finish_line_char} Self total",
            f"= {amount_self}",
            "",
            "",
            style_name="net"
        )

    def _get_split_status_icon(self, split) -> str:
        if split.isPaid:
            return f"[green]{CONFIG.symbols.split_paid}[/green]"
        else:
            return f"[grey]{CONFIG.symbols.split_unpaid}[/grey]"

    def _build_person_view(self, table: DataTable, _) -> None:
        persons = get_persons_with_splits(**self.page_parent.filter)
        
        # Display each person and their splits
        for person in persons:
            if person.splits:  # Person has splits for this month
                # Add person header
                self._add_group_header_row(table, person.name)
                
                # Add splits for this person
                for split in person.splits:
                    record = split.record
                    paid_icon = f"[green]{CONFIG.symbols.split_paid}[/green]" if split.isPaid else f"[red]{CONFIG.symbols.split_unpaid}[/red]"
                    date = format_date_to_readable(split.paidDate) if split.paidDate else "Not paid"
                    record_date = format_date_to_readable(record.date)
                    category = f"[{record.category.color.lower()}]{CONFIG.symbols.category_color}[/{record.category.color.lower()}] {record.category.name}"
                    amount = f"[red]{CONFIG.symbols.amount_negative}[/red] {split.amount}" if record.isIncome else f"[green]{CONFIG.symbols.amount_positive}[/green] {split.amount}"
                    account = split.account.name if split.account else "-"
                    
                    table.add_row(
                        " ",
                        f"{paid_icon} {date}",
                        record_date,
                        category,
                        amount,
                        account,
                        key=f"split-{split.id}"
                    )

    #region Helpers
    # -------------- Helpers ------------- #
        

    #region Callbacks
    # ------------- Callbacks ------------ #    
    
    def watch_displayMode(self, displayMode: DisplayMode) -> None:
        self.query_one("#display-date").classes = "selected" if displayMode == DisplayMode.DATE else ""
        self.query_one("#display-person").classes = "selected" if displayMode == DisplayMode.PERSON else ""
        
    def action_toggle_splits(self) -> None:
        self.show_splits = not self.show_splits
        self.rebuild()
    
    def action_new_record(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_record_and_splits(result['record'], result['splits'])
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:   
                    self.app.notify(title="Success", message=f"Record created", severity="information", timeout=3)
                    self.page_parent.rebuild()
        
        self.app.push_screen(RecordModal("New Record", form=self.record_form.get_form(self.page_parent.mode)), callback=check_result)
    
    def action_edit_record(self) -> None:
        record = get_record_by_id(self.current_row)
        def check_result(result: bool) -> None:
            if result:
                try:
                    update_record_and_splits(self.current_row, result['record'], result['splits'])
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:
                    self.app.notify(title="Success", message=f"Record updated", severity="information", timeout=3)
                    self.page_parent.rebuild()
            else:
                self.app.notify(title="Discarded", message=f"Record not updated", severity="warning", timeout=3)
        
        if record:
            if record.isTransfer:
                self.app.push_screen(TransferModal(record), callback=check_result)
            else:
                filled_form, filled_splits = self.record_form.get_filled_form(record.id)
                self.app.push_screen(RecordModal("Edit Record", form=filled_form, splitForm=filled_splits, isEditing=True), callback=check_result)
        else:
            # might be a split
            if False:
                pass
            else: # utility row
                self.app.notify(title="Utility row", message="Nothing to edit.", severity="warning", timeout=2)

    def action_delete_record(self) -> None:
        def check_delete(result: bool) -> None:
            if result:
                delete_record(self.current_row)
                self.app.notify(title="Success", message=f"Record deleted", severity="information", timeout=3)
                self.page_parent.rebuild()
        self.app.push_screen(ConfirmationModal("Are you sure you want to delete this record?"), check_delete)
    
    def action_new_transfer(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_record(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:
                    self.app.notify(title="Success", message=f"Record created", severity="information", timeout=3)
                    self.page_parent.rebuild()
            else:
                self.app.notify(title="Discarded", message=f"Record not updated", severity="warning", timeout=3)
        if get_accounts_count() > 1:
            self.app.push_screen(TransferModal(), callback=check_result)
        else:
            self.app.notify(title="Error", message="Please have at least two accounts to create a transfer.", severity="error", timeout=2)
        
    def action_display_by_person(self) -> None:
        self.displayMode = DisplayMode.PERSON
        self.rebuild()
        
    def action_display_by_date(self) -> None:
        self.displayMode = DisplayMode.DATE
        self.rebuild()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "prev-month":
                self.page_parent.action_prev_month()
            case "next-month":
                self.page_parent.action_next_month()
            case "display-date":
                self.action_display_by_date()
            case "display-person":
                self.action_display_by_person()
            case _:
                pass
    
    #region View
    # --------------- View --------------- #
        
    def compose(self) -> ComposeResult:
        with Container(classes="selectors"):
            displayContainer = Container(classes="display-selector")
            displayContainer.border_title = "Display by:"
            with displayContainer:
                yield Button(f"([u]{CONFIG.hotkeys.home.display_by_date}[/u]) Date", id="display-date")
                yield Button(f"([u]{CONFIG.hotkeys.home.display_by_person}[/u]) Person", id="display-person")
        self.table =  DataTable(
            id="records-table", 
            cursor_type="row", 
            cursor_foreground_priority=True, 
            zebra_stripes=True,
            additional_classes=["datatable--net-row", "datatable--group-header-row"]   
        )
        yield self.table
        yield EmptyIndicator("No entries")