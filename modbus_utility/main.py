# main.py
import logging
import os

path = os.path.dirname(os.path.abspath(__file__))

import typer

from modbus_utility.application.modbus_commands import select_device, read_register, write_register, list_ports, info

# Set up logging
logging.basicConfig(filename='modbus_utility.log', level=logging.INFO, format='%(asctime)s - %(message)s')

app = typer.Typer()

# Add commands to the app
app.command()(select_device)
app.command()(read_register)
app.command()(write_register)
app.command()(list_ports)
app.command()(info)


if __name__ == "__main__":
    app()
