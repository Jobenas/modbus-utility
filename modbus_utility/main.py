# main.py
import logging
import os

import typer

path = os.path.dirname(os.path.abspath(__file__))


from modbus_utility.info import app as info_app
from modbus_utility.master import app as master_app
from modbus_utility.slave import app as slave_app
from modbus_utility.version import app as version_app


# Set up logging
logging.basicConfig(
    filename="modbus_utility.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

app = typer.Typer()

# Add commands to the app
app.add_typer(info_app, name="info")
app.add_typer(master_app, name="master")
app.add_typer(slave_app, name="slave")
app.add_typer(version_app)


if __name__ == "__main__":
    app()
