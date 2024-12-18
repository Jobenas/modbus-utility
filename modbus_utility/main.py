# main.py
import logging
import os

import typer

path = os.path.dirname(os.path.abspath(__file__))

from modbus_utility.application.modbus_commands import (
    select_device,
    read_register,
    write_register,
    list_ports,
    info,
)
import modbus_utility.slave as slave

# Set up logging
logging.basicConfig(
    filename="modbus_utility.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

app = typer.Typer()

# Add commands to the app

app.command()(select_device)
app.command()(read_register)
app.command()(write_register)
app.command()(list_ports)
app.command()(info)

# app.add_typer(slave, name="slave")


if __name__ == "__main__":
    app()
