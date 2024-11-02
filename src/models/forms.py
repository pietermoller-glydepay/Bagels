from datetime import datetime
from enum import Enum
from typing import Any, List, Optional, Union, Callable

from pydantic import BaseModel, Field, field_validator, model_validator
from rich.text import Text

class FieldOption(BaseModel):
    text: Optional[str] = None
    value: Any
    prefix: Optional[Text] = None
    postfix: Optional[Text] = None
    
    model_config = {"arbitrary_types_allowed": True}
    
    @field_validator('prefix', 'postfix')
    def convert_text_to_str(cls, v):
        if isinstance(v, Text):
            return str(v)
        return v

class FieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    DATE = "date"
    DATE_AUTO_DAY = "dateAutoDay"
    HIDDEN = "hidden"
    AUTOCOMPLETE = "autocomplete"

class FormField(BaseModel):
    title: str
    key: str
    type: FieldType
    placeholder: Optional[str] = ""
    isRequired: bool = False
    defaultValue: Optional[Any] = None
    defaultValueText: Optional[str] = None
    options: List[FieldOption] = []
    min: Optional[float] = None
    max: Optional[float] = None
    labels: Optional[List[str]] = None  # For boolean fields
    create_action: Optional[Callable] = None
    
    model_config = {"arbitrary_types_allowed": True}

    @field_validator('defaultValue')
    def convert_default_value(cls, v):
        if isinstance(v, (int, float)):
            return str(v)
        return v

    @model_validator(mode='after')
    def validate_field_type(self):
        if self.type == FieldType.BOOLEAN and not self.labels:
            raise ValueError("Boolean fields must have labels")
        return self

class RecordFormModel(BaseModel):
    label: FormField = FormField(
        title="Label",
        key="label",
        type=FieldType.STRING,
        placeholder="Label"
    )
    
    categoryId: FormField = FormField(
        title="Category",
        key="categoryId",
        type=FieldType.AUTOCOMPLETE,
        isRequired=True,
        placeholder="Select Category",
        options=[]
    )
    
    amount: FormField = FormField(
        title="Amount",
        key="amount",
        type=FieldType.NUMBER,
        placeholder="0.00",
        min=0,
        isRequired=True
    )
    
    accountId: FormField = FormField(
        title="Account",
        key="accountId",
        type=FieldType.AUTOCOMPLETE,
        isRequired=True,
        placeholder="Select Account",
        options=[]
    )
    
    isIncome: FormField = FormField(
        title="Type",
        key="isIncome",
        type=FieldType.BOOLEAN,
        labels=["Expense", "Income"],
        defaultValue=False
    )
    
    date: FormField = FormField(
        title="Date",
        key="date",
        type=FieldType.DATE_AUTO_DAY,
        placeholder="dd (mm) (yy)",
        defaultValue=datetime.now().strftime("%d")
    )

class SplitFormModel(BaseModel):
    personId: FormField = FormField(
        title="Person",
        key="personId",
        type=FieldType.AUTOCOMPLETE,
        isRequired=True,
        placeholder="Select Person",
        options=[]
    )
    
    amount: FormField = FormField(
        title="Amount",
        key="amount",
        type=FieldType.NUMBER,
        min=0,
        isRequired=True,
        placeholder="0.00"
    )
    
    isPaid: FormField = FormField(
        title="Paid",
        key="isPaid",
        type=FieldType.HIDDEN,
        defaultValue=False
    )
    
    accountId: FormField = FormField(
        title="Paid to account",
        key="accountId",
        type=FieldType.HIDDEN,
        placeholder="Select Account",
        options=[],
        defaultValue=None
    )
    
    paidDate: FormField = FormField(
        title="Paid Date",
        key="paidDate",
        type=FieldType.HIDDEN,
        defaultValue=None
    ) 