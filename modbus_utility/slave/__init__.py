import typer

from modbus_utility.slave.slave_run import app as slave_run_app

app = typer.Typer(help="Modbus slave operation.")

app.add_typer(slave_run_app)
