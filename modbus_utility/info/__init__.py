import typer

from modbus_utility.info.info import app as port_info_app

app = typer.Typer(help="General system information commands")

app.add_typer(port_info_app)
