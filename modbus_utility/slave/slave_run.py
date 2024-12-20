from rich.console import Console
import typer

from modbus_utility.utils.console_utils import format_text_element, TextElement, TextFormat, TextColors
from modbus_utility.utils.modbus_slave import ModbusSlave
from modbus_utility.utils.operation_utils import load_session, DeviceConfigType

app = typer.Typer()

console = Console()


@app.command()
def run(
	show_debug: bool = False
):
	"""Run the MODBUS slave simulator."""
	session = load_session(DeviceConfigType.slave)
	if session is None:
		console.print(
			f"{format_text_element(
				TextElement(
					value="No device selected. Use 'select-device' first.",
					format=TextFormat(color=TextColors.RED, bold=True)
				)
			)}"
		)
		raise typer.Exit()

	modbus_slave = ModbusSlave(
		port=session["port"],
		baudrate=session["baudrate"],
		parity=session["parity"],
		stop_bits=session["stopbits"],
		timeout=session["timeout"],
		slave_address=session["address"],
	)

	modbus_slave.start_listening(show_debug)
