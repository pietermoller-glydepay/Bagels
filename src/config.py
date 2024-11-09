from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class Defaults(BaseModel):
    period: Literal["day", "week", "month", "year"]
    first_day_of_week: int = Field(ge=0, le=6)

class InsightsHotkeys(BaseModel):
    toggle_use_account: str
    
class DatemodeHotkeys(BaseModel):
    go_to_day: str

class HomeHotkeys(BaseModel):
    categories: str
    new_transfer: str 
    toggle_splits: str 
    display_by_date: str
    display_by_person: str
    cycle_offset_type: str
    toggle_income_mode: str
    select_prev_account: str
    select_next_account: str
    insights: InsightsHotkeys
    datemode: DatemodeHotkeys

class RecordModalHotkeys(BaseModel):
    new_split: str  
    new_paid_split: str
    delete_last_split: str


class CategoriesHotkeys(BaseModel):
    new_subcategory: str


class Hotkeys(BaseModel):
    new: str
    delete: str 
    edit: str
    toggle_jump_mode: str
    home: HomeHotkeys
    record_modal: RecordModalHotkeys
    categories: CategoriesHotkeys

class Symbols(BaseModel):
    line_char: str
    finish_line_char: str
    split_paid: str
    split_unpaid: str
    category_color: str
    amount_positive: str
    amount_negative: str

class State(BaseModel):
    theme: str

class Config(YamlBaseSettings):
    hotkeys: Hotkeys
    symbols: Symbols
    model_config = SettingsConfigDict(
        yaml_file="config.yaml",
    )
    defaults: Defaults
    state: State

CONFIG = Config()

def write_state(key: str, value: Any) -> None:
    """Write a state value to the config.yaml file."""
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    config["state"][key] = value
    
    with open("config.yaml", "w") as f:
        yaml.dump(config, f, default_flow_style=False)