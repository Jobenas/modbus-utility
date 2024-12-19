from rich.table import Table
import typer

from modbus_utility.utils.console_utils import format_text_element, TextElement, TextFormat, TextColors, generate_table
from modbus_utility.utils.operation_utils import DeviceConfigType, save_session, load_session


def set_device_config(
	port: str,
	address: int,
	baudrate: int = 9600,
	parity: str = "N",
	stopbits: int = 1,
	timeout: float = 1.0,
	config_type: DeviceConfigType = DeviceConfigType.master
) -> None:
	"""
	Saves the configuration file to a specific configuration file for master or slave.
	:param port: serial port to use.
	:param address: address of the slave device.
	:param baudrate: baud rate to use for the communication.
	:param parity: parity configuration for the communication.
	:param stopbits: stop bits configuration for the communication.
	:param timeout: timeout for the communication.
	:param config_type: type of configuration to save, it can be slave or master.
	:return: None
	"""
	session_data = {
		"port": port,
		"address": address,
		"baudrate": baudrate,
		"parity": parity,
		"stopbits": stopbits,
		"timeout": timeout,
	}

	save_session(session_data, config_type)
	print(
		f"Selected device at address "
		f"{format_text_element(
			TextElement(
				value=address,
				format=TextFormat(color=TextColors.CYAN, bold=True)
			)
		)} on port "
		f"{format_text_element(
			TextElement(
				value=port,
				format=TextFormat(color=TextColors.GREEN, bold=True)
			)
		)}"
	)


def get_device_config(config_type: DeviceConfigType) -> Table:
	"""
	Generates a table element with the all the device's configuration present.
	:param config_type: type of configuration to generate: can be master or slave.
	:return: table element with all the configuration generated.
	"""
	session = load_session(config_type)
	if session is None:
		print(
			f"{format_text_element(
				TextElement(
					value='No device selected. Use `master select-device` first.',
					format=TextFormat(color=TextColors.RED, bold=True)
				)
			)}"
		)
		raise typer.Exit()

	print(
		f"{format_text_element(
			TextElement(
				value='Current device configuration: ',
				format=TextFormat(color=TextColors.GREEN, bold=True)
			)
		)}"
	)
	table = generate_table(
		columns=[TextElement(value="PARAMETER"), TextElement(value="VALUE")],
		rows=[
			[
				TextElement(value="PORT"),
				TextElement(
					value=session["port"], format=TextFormat(color=TextColors.GREEN)
				),
			],
			[
				TextElement(value="ADDRESS"),
				TextElement(
					value=session["address"], format=TextFormat(color=TextColors.GREEN)
				),
			],
			[
				TextElement(value="BAUD RATE"),
				TextElement(
					value=session["baudrate"], format=TextFormat(color=TextColors.GREEN)
				),
			],
			[
				TextElement(value="PARITY"),
				TextElement(
					value=session["parity"], format=TextFormat(color=TextColors.GREEN)
				),
			],
			[
				TextElement(value="STOP BITS"),
				TextElement(
					value=session["stopbits"], format=TextFormat(color=TextColors.GREEN)
				),
			],
			[
				TextElement(value="TIMEOUT"),
				TextElement(
					value=session["timeout"], format=TextFormat(color=TextColors.GREEN)
				),
			],
		],
	)

	return table
