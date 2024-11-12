from pathlib import Path

import click
import yaml

from bagels.config import Config
from bagels.locations import config_file, database_file, set_custom_root
from bagels.models.database.app import init_db

import threading
import time
from bagels.bagel import render_frame, pprint, theta_spacing, phi_spacing


def create_config_file() -> None:
    f = config_file()
    if f.exists():
        return

    try:
        f.touch()
        with open(f, "w") as f:
            yaml.dump(Config.get_default().model_dump(), f)
    except OSError:
        pass


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

        # Flag to control the donut animation
        stop_animation = threading.Event()

        def animate_donut():
            A = B = 1
            while not stop_animation.is_set():
                A += theta_spacing
                B += phi_spacing
                print("\x1b[H\x1b[2J")  # Clear screen
                pprint(render_frame(A, B))
                time.sleep(0.1)

        # Start donut animation in a separate thread
        donut_thread = threading.Thread(target=animate_donut)
        donut_thread.start()

        # Perform initialization
        create_config_file()
        init_db()

        from bagels.app import App

        app = App()

        # Stop the animation
        stop_animation.set()
        donut_thread.join()
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
