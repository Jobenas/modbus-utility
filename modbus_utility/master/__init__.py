import typer

from modbus_utility.master.read_registers import app as read_register_app
from modbus_utility.master.write_registers import app as write_register_app

app = typer.Typer(help="Modbus master operation.")

app.add_typer(read_register_app)
app.add_typer(write_register_app)
