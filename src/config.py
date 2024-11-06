from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class InsightsHotkeys(BaseModel):
    toggle_use_account: str

class HomeHotkeys(BaseModel):
    new_transfer: str 
    toggle_splits: str 
    display_by_date: str
    display_by_person: str
    cycle_offset_type: str
    toggle_income_mode: str
    select_prev_account: str
    select_next_account: str
    toggle_jump_mode: str
    insights: InsightsHotkeys

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

class Config(YamlBaseSettings):
    hotkeys: Hotkeys
    symbols: Symbols
    model_config = SettingsConfigDict(
        yaml_file="config.yaml",
    )


CONFIG = Config()