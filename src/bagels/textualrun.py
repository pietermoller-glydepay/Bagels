# file is used with textual run --dev


if __name__ == "__main__":
    from bagels.config import load_config

    load_config()

    from bagels.models.database.app import init_db

    init_db()

    from bagels.app import App

    app = App()
    app.run()
