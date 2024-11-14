# file is used with textual run --dev

from pathlib import Path
from bagels.locations import set_custom_root
from bagels.models.database.app import init_db

if __name__ == "__main__":
    # set_custom_root(Path("./instance/"))
    init_db()
    from bagels.app import App

    app = App()
    app.run()
