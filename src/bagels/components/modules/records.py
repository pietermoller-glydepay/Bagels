from datetime import datetime, timedelta

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Static

from textual.widgets import Button
from bagels.components.datatable import DataTable
from bagels.components.indicators import EmptyIndicator
from bagels.modals.confirmation import ConfirmationModal
from bagels.modals.record import RecordModal
from bagels.modals.transfer import TransferModal
from bagels.modals.input import InputModal
from bagels.config import CONFIG
from bagels.managers.persons import (
    get_person_by_id,
    get_persons_with_splits,
    update_person,
)
from bagels.managers.records import (
    create_record,
    create_record_and_splits,
    delete_record,
    get_record_by_id,
    get_record_total_split_amount,
    get_records,
    update_record,
    update_record_and_splits,
)
from bagels.managers.splits import get_split_by_id, update_split
from bagels.forms.form import Form
from bagels.utils.format import format_date_to_readable
from bagels.forms.person_forms import PersonForm
from bagels.forms.record_forms import RecordForm


class DisplayMode:
    DATE = "d"
    PERSON = "p"


class Records(Static):
    BINDINGS = [
        (CONFIG.hotkeys.new, "new", "Add"),
        (CONFIG.hotkeys.delete, "delete", "Delete"),
        (CONFIG.hotkeys.edit, "edit", "Edit"),
        (CONFIG.hotkeys.home.new_transfer, "new_transfer", "Transfer"),
        (CONFIG.hotkeys.home.toggle_splits, "toggle_splits", "Toggle Splits"),
        Binding(
            CONFIG.hotkeys.home.display_by_person,
            "display_by_person",
            "Display by Person",
            show=False,
        ),
        Binding(
            CONFIG.hotkeys.home.display_by_date,
            "display_by_date",
            "Display by Date",
            show=False,
        ),
    ]

    can_focus = True
    show_splits = True
    displayMode = reactive(DisplayMode.DATE)

    def __init__(self, parent: Static, *args, **kwargs) -> None:
        super().__init__(
            *args, **kwargs, id="records-container", classes="module-container"
        )
        super().__setattr__("border_title", "Records")
        self.page_parent = parent
        self.record_form = RecordForm()
        self.person_form = PersonForm()

    def on_mount(self) -> None:
        self.rebuild()

    # ---------- Table builders ---------- #
    # region Table

    def rebuild(self) -> None:
        if not hasattr(self, "table"):
            return
        table = self.table
        empty_indicator: EmptyIndicator = self.query_one("#empty-indicator")
        self._initialize_table(table)
        records = self._fetch_records()

        match self.displayMode:
            case DisplayMode.PERSON:
                self._build_person_view(table, records)
            case DisplayMode.DATE:
                self._build_date_view(table, records)
            case _:
                pass

        table.focus()
        if hasattr(self, "current_row_index"):
            table.move_cursor(row=self.current_row_index)
        empty_indicator.display = not table.rows

    def _fetch_records(self):
        if self.page_parent.filter["byAccount"]:
            return get_records(
                offset=self.page_parent.filter["offset"],
                offset_type=self.page_parent.filter["offset_type"],
                account_id=self.page_parent.mode["accountId"]["default_value"],
            )
        else:
            return get_records(
                offset=self.page_parent.filter["offset"],
                offset_type=self.page_parent.filter["offset_type"],
            )

    def _initialize_table(self, table: DataTable) -> None:
        table.clear()
        table.columns.clear()
        match self.displayMode:
            case DisplayMode.PERSON:
                table.add_columns(
                    " ", "Date", "Record date", "Category", "Amount", "Paid to account"
                )
            case DisplayMode.DATE:
                table.add_columns(" ", "Category", "Amount", "Label", "Account")

    # region Date view
    def _build_date_view(self, table: DataTable, records: list) -> None:
        prev_group = None
        for record in records:
            flow_icon = self._get_flow_icon(len(record.splits) > 0, record.isIncome)

            category_string, amount_string, account_string = self._format_record_fields(
                record, flow_icon
            )
            label_string = record.label if record.label else "-"

            # Add group header based on filter type
            group_string = None
            match self.page_parent.filter["offset_type"]:
                case "year":
                    # Group by month
                    group_string = record.date.strftime("%B %Y")
                case "month":
                    # Group by week
                    week_start = record.date - timedelta(
                        days=(record.date.weekday() - CONFIG.defaults.first_day_of_week)
                        % 7
                    )
                    week_end = week_start + timedelta(days=6)

                    # Adjust week_start and week_end if they are not in the same month as record.date
                    if week_start.month != record.date.month:
                        week_start = record.date.replace(day=1)
                    if week_end.month != record.date.month:
                        last_day_of_month = (
                            record.date.replace(day=1) + timedelta(days=32)
                        ).replace(day=1) - timedelta(days=1)
                        week_end = last_day_of_month

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
                account_string,
                key=f"r-{str(record.id)}",
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

    def _format_record_fields(self, record, flow_icon: str) -> tuple[str, str]:
        if record.isTransfer:
            from_account = (
                "[italic]" + record.account.name + "[/italic]"
                if record.account.hidden
                else record.account.name
            )
            to_account = (
                "[italic]" + record.transferToAccount.name + "[/italic]"
                if record.transferToAccount.hidden
                else record.transferToAccount.name
            )
            category_string = f"{from_account} → {to_account}"
            amount_string = record.amount
            account_string = "-"
        else:
            color_tag = record.category.color.lower()
            category_string = f"[{color_tag}]{CONFIG.symbols.category_color}[/{color_tag}] {record.category.name}"

            if record.splits and not self.show_splits:
                amount_self = round(
                    record.amount - get_record_total_split_amount(record.id)
                )
                amount_string = f"{flow_icon} {amount_self}"
            else:
                amount_string = f"{flow_icon} {record.amount}"

            account_string = record.account.name

        return category_string, amount_string, account_string

    def _add_group_header_row(
        self, table: DataTable, string: str, key: str = None
    ) -> None:
        table.add_row("//", string, "", "", "", style_name="group-header", key=key)

    def _add_split_rows(self, table: DataTable, record, flow_icon: str) -> None:
        color = record.category.color.lower()
        amount_self = round(record.amount - get_record_total_split_amount(record.id), 2)
        split_flow_icon = (
            f"[red]{CONFIG.symbols.amount_negative}[/red]"
            if record.isIncome
            else f"[green]{CONFIG.symbols.amount_positive}[/green]"
        )
        line_char = f"[{color}]{CONFIG.symbols.line_char}[/{color}]"
        finish_line_char = f"[{color}]{CONFIG.symbols.finish_line_char}[/{color}]"

        for split in record.splits:
            paid_status_icon = self._get_split_status_icon(split)
            date_string = (
                Text(f"Paid {format_date_to_readable(split.paidDate)}", style="italic")
                if split.paidDate
                else Text("-")
            )

            table.add_row(
                " ",
                f"{line_char} {paid_status_icon} {split.person.name}",
                f"{split_flow_icon} {split.amount}",
                date_string,
                split.account.name if split.account else "-",
                key=f"s-{str(split.id)}",
            )

        # Add net amount row
        table.add_row(
            "",
            f"{finish_line_char} Self total",
            f"= {amount_self}",
            "",
            "",
            style_name="net",
        )

    def _get_split_status_icon(self, split) -> str:
        if split.isPaid:
            return f"[green]{CONFIG.symbols.split_paid}[/green]"
        else:
            return f"[grey]{CONFIG.symbols.split_unpaid}[/grey]"

    # region Person view
    def _build_person_view(self, table: DataTable, _) -> None:
        persons = get_persons_with_splits(
            offset=self.page_parent.filter["offset"],
            offset_type=self.page_parent.filter["offset_type"],
        )

        # Display each person and their splits
        for person in persons:
            if person.splits:  # Person has splits for this month
                # Add person header
                self._add_group_header_row(
                    table, person.name, key=f"p-{str(person.id)}"
                )

                # Add splits for this person
                for split in person.splits:
                    record = split.record
                    paid_icon = (
                        f"[green]{CONFIG.symbols.split_paid}[/green]"
                        if split.isPaid
                        else f"[red]{CONFIG.symbols.split_unpaid}[/red]"
                    )
                    date = (
                        format_date_to_readable(split.paidDate)
                        if split.paidDate
                        else "Not paid"
                    )
                    record_date = format_date_to_readable(record.date)
                    category = f"[{record.category.color.lower()}]{CONFIG.symbols.category_color}[/{record.category.color.lower()}] {record.category.name}"
                    amount = (
                        f"[red]{CONFIG.symbols.amount_negative}[/red] {split.amount}"
                        if record.isIncome
                        else f"[green]{CONFIG.symbols.amount_positive}[/green] {split.amount}"
                    )
                    account = f"→ {split.account.name}" if split.account else "-"

                    table.add_row(
                        " ",
                        f"{paid_icon} {date}",
                        record_date,
                        category,
                        amount,
                        account,
                        key=f"s-{split.id}",
                    )

    # region Helpers
    # -------------- Helpers ------------- #

    # region Callbacks
    # ------------- Callbacks ------------ #

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        current_row_index = event.cursor_row
        if event.row_key and event.row_key.value:
            self.current_row = event.row_key.value
            self.current_row_index = current_row_index
        else:
            self.current_row = None
            self.current_row_index = None

    def watch_displayMode(self, displayMode: DisplayMode) -> None:
        self.query_one("#display-date").classes = (
            "selected" if displayMode == DisplayMode.DATE else ""
        )
        self.query_one("#display-person").classes = (
            "selected" if displayMode == DisplayMode.PERSON else ""
        )

    def action_toggle_splits(self) -> None:
        self.show_splits = not self.show_splits
        self.rebuild()

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

    # region cud

    def action_new(self) -> None:
        def check_result(result) -> None:
            if result:
                try:
                    create_record_and_splits(result["record"], result["splits"])
                except Exception as e:
                    self.app.notify(
                        title="Error", message=f"{e}", severity="error", timeout=10
                    )
                else:
                    self.app.notify(
                        title="Success",
                        message=f"Record created",
                        severity="information",
                        timeout=3,
                    )
                    self.page_parent.rebuild()

        date = format_date_to_readable(self.page_parent.mode["date"])
        account_name = self.page_parent.mode["accountId"]["default_value_text"]
        type = "Income" if self.page_parent.mode["isIncome"] else "Expense"
        self.app.push_screen(
            RecordModal(
                f"New {type} on {account_name} for {date}",
                form=self.record_form.get_form(self.page_parent.mode),
                splitForm=Form(),
                date=self.page_parent.mode["date"],
            ),
            callback=check_result,
        )

    def action_edit(self) -> None:
        if not (hasattr(self, "current_row") and self.current_row):
            self.app.notify(
                title="Error", message="Nothing selected", severity="error", timeout=2
            )
            self.app.bell()
            return
        # ----------------- - ---------------- #
        type = self.current_row.split("-")[0]
        id = self.current_row.split("-")[1]

        # ----------------- - ---------------- #
        def check_result_records(result) -> None:
            if result:
                try:
                    if result.get("record"):  # if not editing a transfer:
                        update_record_and_splits(id, result["record"], result["splits"])
                    else:
                        update_record(id, result)
                except Exception as e:
                    self.app.notify(
                        title="Error", message=f"{e}", severity="error", timeout=10
                    )
                else:
                    self.app.notify(
                        title="Success",
                        message=f"Record updated",
                        severity="information",
                        timeout=3,
                    )
                    self.page_parent.rebuild()
            else:
                self.app.notify(
                    title="Discarded",
                    message=f"Record not updated",
                    severity="warning",
                    timeout=3,
                )

        def check_result_person(result) -> None:
            if result:
                try:
                    update_person(id, result)
                except Exception as e:
                    self.app.notify(
                        title="Error", message=f"{e}", severity="error", timeout=10
                    )
                else:
                    self.app.notify(
                        title="Success",
                        message=f"Person updated",
                        severity="information",
                        timeout=3,
                    )
                    self.page_parent.rebuild()
            else:
                self.app.notify(
                    title="Discarded",
                    message=f"Person not updated",
                    severity="warning",
                    timeout=3,
                )

        # ----------------- - ---------------- #
        match type:
            case "r":
                record = get_record_by_id(id)
                if not record:
                    self.app.notify(
                        title="Error",
                        message="Record not found",
                        severity="error",
                        timeout=2,
                    )
                    return
                if record.isTransfer:
                    self.app.push_screen(
                        TransferModal(record), callback=check_result_records
                    )
                else:
                    filled_form, filled_splits = self.record_form.get_filled_form(
                        record.id
                    )
                    self.app.push_screen(
                        RecordModal(
                            "Edit Record",
                            form=filled_form,
                            splitForm=filled_splits,
                            isEditing=True,
                        ),
                        callback=check_result_records,
                    )
            case "s":
                split = get_split_by_id(id)
                if split.isPaid:
                    split_data = {"accountId": None, "isPaid": False, "paidDate": None}
                    update_split(id, split_data)
                    self.app.notify(
                        title="Reverted split",
                        message=f"Marked this split as unpaid",
                        severity="information",
                        timeout=3,
                    )
                else:
                    split_data = {
                        "accountId": self.page_parent.mode["accountId"][
                            "default_value"
                        ],
                        "isPaid": True,
                        "paidDate": datetime.now(),
                    }
                    update_split(id, split_data)
                    self.app.notify(
                        title="Completed split",
                        message=f"With account {self.page_parent.mode['accountId']['default_value_text']} today",
                        severity="information",
                        timeout=3,
                    )
                self.page_parent.rebuild()
            case "p":
                person = get_person_by_id(id)
                if not person:
                    self.app.notify(
                        title="Error",
                        message="Person not found",
                        severity="error",
                        timeout=2,
                    )
                    return
                self.app.push_screen(
                    InputModal(
                        "Edit Person", form=self.person_form.get_filled_form(person.id)
                    ),
                    callback=check_result_person,
                )
            case _:
                pass

    def action_delete(self) -> None:
        if not (hasattr(self, "current_row") and self.current_row):
            self.app.notify(
                title="Error", message="Nothing selected", severity="error", timeout=2
            )
            self.app.bell()
            return
        # ----------------- - ---------------- #
        type = self.current_row.split("-")[0]
        id = self.current_row.split("-")[1]

        if type == "s":
            self.app.notify(
                title="Error",
                message="You cannot delete or add splits to a record after creation.",
                severity="error",
                timeout=2,
            )
            return

        # ----------------- - ---------------- #
        def check_delete(result) -> None:
            if result:
                delete_record(id)
                self.app.notify(
                    title="Success",
                    message=f"Record deleted",
                    severity="information",
                    timeout=3,
                )
                self.page_parent.rebuild()

        # ----------------- - ---------------- #
        match type:
            case "r":
                self.app.push_screen(
                    ConfirmationModal("Are you sure you want to delete this record?"),
                    callback=check_delete,
                )
            case "s":
                self.app.push_screen(
                    ConfirmationModal("Are you sure you want to delete this split?"),
                    callback=check_delete,
                )
            case _:
                pass

    def action_new_transfer(self) -> None:
        def check_result(result) -> None:
            if result:
                try:
                    create_record(result)
                except Exception as e:
                    self.app.notify(
                        title="Error", message=f"{e}", severity="error", timeout=10
                    )
                else:
                    self.app.notify(
                        title="Success",
                        message=f"Record created",
                        severity="information",
                        timeout=3,
                    )
                    self.page_parent.rebuild()
            else:
                self.app.notify(
                    title="Discarded",
                    message=f"Record not updated",
                    severity="warning",
                    timeout=3,
                )

        self.app.push_screen(TransferModal(), callback=check_result)

    # region View
    # --------------- View --------------- #

    def compose(self) -> ComposeResult:
        with Container(classes="selectors"):
            displayContainer = Container(classes="display-selector")
            displayContainer.border_title = "Display by:"
            displayContainer.border_subtitle = f"{CONFIG.hotkeys.home.display_by_date} {CONFIG.hotkeys.home.display_by_person}"
            with displayContainer:
                yield Button(f"Date", id="display-date")
                yield Button(f"Person", id="display-person")
        self.table = DataTable(
            id="records-table",
            cursor_type="row",
            cursor_foreground_priority=True,
            zebra_stripes=True,
            additional_classes=["datatable--net-row", "datatable--group-header-row"],
        )
        yield self.table
        yield EmptyIndicator("No entries")
