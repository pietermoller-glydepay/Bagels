from textual.app import ComposeResult
from textual.widgets import Static, DataTable, Label, Rule
from textual.containers import Horizontal, Container
from components.base import BasePage
from components.modals import ConfirmationModal
from components.base import BasePage
from components.home.modals import NewRecordModal
from controllers.records import getRecordTableRows

class Page(Static):
    def on_mount(self) -> None:
        self.build_table()

    # ------------- Callbacks ------------ #
    
    def build_table(self) -> None:
        table = self.query_one("#records-table")
        table.clear()
        if not table.columns:
            table.add_columns("T", "Date", "Category", "Amount", "Label")
        # table.add_rows(getRecordTableRows())
        table.cursor_type = 'cell'
        table.zebra_stripes = True
        table.focus()
    
    def action_newRecords(self) -> None:
        def checkResult(result: bool) -> None:
            if result:
                pass
        
        self.app.push_screen(NewRecordModal(), callback=checkResult)
        pass

    def action_deleteRecord(self) -> None:
        def checkDelete(result: bool) -> None:
            if result:
                self.mount(Label("Deleted"))
        
        self.app.push_screen(ConfirmationModal("Are you sure you want to delete this record?"), checkDelete)

    # --------------- View --------------- #
    
    def compose(self) -> ComposeResult:
        self.basepage = BasePage(
            pageName="Home",
            bindings=[
                ("ctrl+n", "newRecords", "New Records", self.action_newRecords), 
            ],
        )
        with self.basepage:
            with Horizontal(classes="home-accounts-list"):
                for i in range(5):
                    with Container(classes="account-container"):
                        yield Label(f"[bold]ACCOUNT NAME {i}[/bold]", classes="account-name", markup=True)
                        yield Label(f"${i}", classes="account-balance")
            yield Rule(classes="home-divider", line_style="double")
            yield DataTable(id="records-table")
