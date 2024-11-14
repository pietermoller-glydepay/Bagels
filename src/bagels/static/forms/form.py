from typing import Any, List, Union, Literal
from pydantic import BaseModel, Field
from rich.console import RenderableType


class Option(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    text: Union[str, None] = None  # if not provided, the value will be used
    value: Any
    prefix: Union[RenderableType, None] = None
    postfix: Union[RenderableType, None] = None


class Options(BaseModel):
    items: List[Option] = Field(default_factory=list)

    def __len__(self):
        return len(self.items)


class FormField(BaseModel):
    placeholder: Union[str, None] = None
    title: str
    key: str
    type: Literal[
        "string",
        "number",
        "integer",
        "boolean",
        "autocomplete",
        "dateAutoDay",
        "hidden",
    ]
    is_required: bool = False
    min: Union[float, int, None] = None
    max: Union[float, int, None] = None
    labels: Union[List[str], None] = None  # for type "boolean"
    options: Union[Options, None] = None  # for type "autocomplete"
    default_value: Any = None
    default_value_text: Union[str, None] = None
    create_action: Union[bool, None] = None  # for type "autocomplete"


class Form(BaseModel):
    fields: List[FormField] = Field(default_factory=list)

    def __len__(self):
        return len(self.fields)
