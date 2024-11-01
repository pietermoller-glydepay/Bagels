from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_yaml import YamlBaseSettings


class HomeHotkeys(BaseModel):
    new_transfer: str 
    toggle_splits: str 


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


class Config(YamlBaseSettings):
    hotkeys: Hotkeys
    
    model_config = SettingsConfigDict(yaml_file="config.yaml")


CONFIG = Config()