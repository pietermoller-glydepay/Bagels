from pathlib import Path

# from venv import create

import click

from bagels.locations import config_file, database_file, set_custom_root


@click.group(invoke_without_command=True)
@click.option(
    "--at",
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=Path),
    help="Specify the path.",
)
@click.pass_context
def cli(ctx, at: click.Path | None):
    """Bagels CLI."""
    if at:
        set_custom_root(at)
    if ctx.invoked_subcommand is None:

        from bagels.config import load_config

        load_config()

        from bagels.models.database.app import init_db

        init_db()

        from bagels.app import App

        app = App()
        app.run()


@cli.command()
@click.argument("thing_to_locate", type=click.Choice(["config", "database"]))
def locate(thing_to_locate: str) -> None:
    if thing_to_locate == "config":
        print("Config file:")
        print(config_file())
    elif thing_to_locate == "database":
        print("Database file:")
        print(database_file())


if __name__ == "__main__":
    cli()
