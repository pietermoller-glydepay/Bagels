from datetime import timedelta

from rich.text import Text

from bagels.components.datatable import DataTable
from bagels.components.indicators import EmptyIndicator
from bagels.config import CONFIG
from bagels.managers.persons import (
    get_persons_with_splits,
)
from bagels.managers.records import (
    get_record_total_split_amount,
    get_records,
)
from bagels.utils.format import format_date_to_readable


class DisplayMode:
    DATE = "d"
    PERSON = "p"


class RecordTableBuilder:

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
                    record.amount - get_record_total_split_amount(record.id), 2
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
        amount_self = round(
            record.amount - get_record_total_split_amount(record.id),
            CONFIG.defaults.round_decimals,
        )
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
                total_unpaid = 0  # Initialize total unpaid amount for this person
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

                    # Calculate amount and update total of unpaid amounts
                    if not split.isPaid:
                        split_amount = split.amount
                        if record.isIncome:
                            split_amount = -split_amount  # Negate income amounts
                        total_unpaid += split_amount

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

                # Add total row for this person showing unpaid amount. We reverse the color indicator.
                if total_unpaid == 0:
                    total_display = "0.0"
                elif total_unpaid < 0:
                    total_display = f"[green]{abs(total_unpaid)}[/green]"
                else:
                    total_display = f"[red]{abs(total_unpaid)}[/red]"
                table.add_row(
                    " ",
                    "[bold]Total Unpaid[/bold]",
                    "",
                    "",
                    f"[bold]{total_display}[/bold]",
                    "",
                    key=f"t-{str(person.id)}",
                )
