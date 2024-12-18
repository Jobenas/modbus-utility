from rich.console import Console
import typer

from modbus_utility.physical.modbus_serial import list_serial_ports

app = typer.Typer()


console = Console()


@app.command()
def list_ports():
	"""
	List available serial ports.
	:return:
	"""
	ports = list_serial_ports()


