from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, HorizontalScroll
from textual.widgets import Label, Static

from bagels.components.modals import ConfirmationModal, InputModal
from bagels.config import CONFIG
from bagels.models.record_template import RecordTemplate
from bagels.queries.record_templates import (create_template, delete_template,
                                             get_all_templates,
                                             update_template)
from bagels.queries.records import create_record
from bagels.utils.recordtemplate_forms import RecordTemplateForm


class Templates(Static):
    can_focus = True
    
    BINDINGS = [
        Binding(CONFIG.hotkeys.new, "new_template", "New Template"),
        Binding(CONFIG.hotkeys.edit, "edit_template", "Edit Template"),
        Binding(CONFIG.hotkeys.delete, "delete_template", "Delete Template"),
    ]
    
    def __init__(self, parent: Static, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs, id="templates-container", classes="module-container")
        super().__setattr__("border_title", "Templates")
        super().__setattr__("border_subtitle",  "1 - 9")
        self.page_parent = parent
        self.templates: list[RecordTemplate] = []
        self.template_form = RecordTemplateForm()
        self.selected_template_id = None
        
    def on_mount(self) -> None:
        self.rebuild()
    
    #region Builder
    # -------------- Builder ------------- #
    
    def _create_templates_widgets(self, container: Container) -> None:
        if len(self.templates) == 0:
            widget = Label("No templates. Jump here to create one.", classes="empty")
            container.compose_add_child(widget)
            return container
        for index, template in enumerate(self.templates):
            if index > 8:
                break
            color = template.category.color
            widget = Container(
                Label(f"[{color}]{CONFIG.symbols.category_color}[/{color}]", classes="dot"),
                Label(f"{template.label}", classes="label"),
                id=f"template-{template.id}",
                classes="template-item"
            )
            widget.border_subtitle = str(index + 1)
            widget.can_focus = True
            container.compose_add_child(widget)
        return container
    
    def rebuild(self) -> None:
        self.templates = get_all_templates()
        container = self.query(".templates")
        if len(container) > 0:
            container[0].remove()
        container = Horizontal(classes="templates")
        container = self._create_templates_widgets(container)
        self.mount(container)
    
    # ------------- Callback ------------- #
    
    def on_descendant_focus(self, event: events.DescendantFocus):
        id = event.widget.id
        if id:
            template_id = id.split("-")[1]
            self.selected_template_id = template_id
        
    def select_template(self, index: int) -> None:
        if index > len(self.templates):
            self.app.notify(title="Error", message=f"Template slot {index} is empty", severity="error", timeout=3)
            return
        template = self.templates[index - 1]
        record_data = template.to_dict()
        record_data["date"] = self.page_parent.mode["date"]
        create_record(record_data)
        self.app.notify(title="Success", message=f"Created new record with {template.label}", severity="information", timeout=3)
        self.page_parent.rebuild()
    
    def action_new_template(self) -> None:
        def check_result(result: bool) -> None:
            if result:
                try:
                    create_template(result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:   
                    self.app.notify(title="Success", message=f"Template created", severity="information", timeout=3)
                    self.rebuild()
        
        self.app.push_screen(InputModal("New Template", form=self.template_form.get_form()), callback=check_result)
    
    def action_edit_template(self) -> None:
        if not self.selected_template_id:
            self.app.notify(title="Error", message="No template selected", severity="error", timeout=3)
            return
        # ----------------- - ---------------- #
        def check_result(result: bool) -> None:
            if result:
                try:
                    update_template(self.selected_template_id, result)
                except Exception as e:
                    self.app.notify(title="Error", message=f"{e}", severity="error", timeout=10)
                else:   
                    self.app.notify(title="Success", message=f"Template created", severity="information", timeout=3)
                    self.rebuild()
        # ----------------- - ---------------- #
        self.app.push_screen(InputModal("Edit Template", form=self.template_form.get_filled_form(self.selected_template_id)), callback=check_result)
    
    def action_delete_template(self) -> None:
        if not self.selected_template_id:
            self.app.notify(title="Error", message="No template selected", severity="error", timeout=3)
            return
        # ----------------- - ---------------- #
        def check_delete(result: bool) -> None:
            if result:
                delete_template(self.selected_template_id)
                self.app.notify(title="Success", message=f"Template deleted", severity="information", timeout=3)
                self.rebuild()
        # ----------------- - ---------------- #
        self.app.push_screen(ConfirmationModal("Are you sure you want to delete this template?"), check_delete)