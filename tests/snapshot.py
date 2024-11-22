import pytest
from textual.pilot import Pilot

from bagels.locations import set_custom_root

APP_PATH = "../src/bagels/app.py"

set_custom_root("./instance/")


def test_loads(snap_compare):
    assert snap_compare(APP_PATH, terminal_size=(140, 40))
