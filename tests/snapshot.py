import time
import pytest

import os
import time_machine
import datetime as dt
from zoneinfo import ZoneInfo

from textual.pilot import Pilot

hill_valley_tz = ZoneInfo("America/Los_Angeles")

TEMP_INSTANCE_PATH = os.path.join(os.path.dirname(__file__), "../instance/")
SIZE_BASIC = (140, 30)
SIZE_VERTICAL = (70, 50)
SIZE_TEST = (140, 30)
APP_PARAMS = {"is_testing": True}


# ---------- Clear last test --------- #

if os.path.exists(TEMP_INSTANCE_PATH):
    for file in os.listdir(TEMP_INSTANCE_PATH):
        os.remove(os.path.join(TEMP_INSTANCE_PATH, file))

# --------- Init app sequence -------- #
from bagels.locations import set_custom_root

set_custom_root(TEMP_INSTANCE_PATH)

from bagels.config import load_config

load_config()

from bagels.models.database.app import init_db

init_db()

from bagels.app import App

# -------------- Freeze -------------- #


@pytest.fixture(autouse=True)
def travel_to_hill_valley_time():
    with time_machine.travel(dt.datetime(1985, 10, 26, 1, 24, tzinfo=hill_valley_tz)):
        yield  # This allows the tests to run within the context of the travel


# --------------- Basic -------------- #


class TestBasic:
    def test_welcome(self, snap_compare):
        assert snap_compare(App(**APP_PARAMS), terminal_size=SIZE_BASIC)

    def test_new_acc_welcome(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_BASIC,
            press=["a", "t", "tab", *"123.45", "enter"],
        )

    def test_vertical_layout(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_VERTICAL,
        )

    def test_jump_screen(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_BASIC,
            press=["v"],
        )


# ------------- Accounts ------------- #


class TestAccounts:
    def test_acc_screen(self, snap_compare):
        assert snap_compare(App(**APP_PARAMS), terminal_size=SIZE_TEST, press=["a"])

    def test_new_acc_home(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_TEST,
            press=["v", "a", "a", "t", "2", "tab", "enter"],
        )

    def test_delete_acc(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_TEST,
            press=["v", "a", "d", "enter"],
        )

    def test_edit_acc(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_TEST,
            press=["v", "a", "e", "tab", *"123.234", "enter"],
        )


# ------------ Categories ------------ #


class TestCategories:
    def test_categories(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_TEST,
            press=["c"],
        )

    def test_new_category_screen(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_TEST,
            press=["c", "a"],
        )

    def test_new_category(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_TEST,
            press=[
                "c",
                "a",
                "t",
                "tab",
                "tab",
                "tab",
                "enter",
            ],  # todo: scroll bottom to see new cat
        )

    def test_new_category_subcategory(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_TEST,
            press=["c", "up", "s", "t", "tab", "tab", "tab", "enter"],
        )

    def test_delete_category(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_TEST,
            press=["c", "d", "enter"],
        )


# ------------- Templates ------------ #


class TestTemplates:
    def test_templates(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_TEST,
            press=[
                "v",
                "t",
                "a",
                "t",
                "tab",
                "tab",
                *"123",
                "tab",
                "tab",
                "space",
                "enter",
            ],
        )

    def test_edit_template(self, snap_compare):
        assert snap_compare(
            App(**APP_PARAMS),
            terminal_size=SIZE_TEST,
            press=["v", "t", "tab", "e", *"est", "enter"],
        )
