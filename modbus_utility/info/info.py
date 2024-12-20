from rich import print
from rich.console import Console
import typer

from modbus_utility.physical.modbus_serial import (
    list_serial_ports,
    initialize_device,
)
from modbus_utility.utils.console_utils import (
    generate_table,
    TextElement,
    TextFormat,
    TextColors,
    format_text_element,
)
from modbus_utility.utils.device_config_utils import (
    set_device_config,
    get_device_config,
)
from modbus_utility.utils.operation_utils import DeviceConfig, DeviceConfigType

console = Console()

app = typer.Typer()


@app.command()
def list_ports():
    """List all available serial ports."""
    ports = list_serial_ports()
    if ports:
        console.print("[bold magenta]Available serial ports:")

        table = generate_table(
            [TextElement(value="PORT"), TextElement(value="DESCRIPTION")],
            [
                [
                    TextElement(
                        value=port.device,
                        format=TextFormat(color=TextColors.BLUE, bold=True),
                    ),
                    TextElement(
                        value=port.description,
                        format=TextFormat(color=TextColors.GREEN, bold=True),
                    ),
                ]
                for port in ports
            ],
        )

        console.print(table)
    else:
        console.print(f"{format_text_element(
            TextElement(
                value="No serial ports found.", 
                format=TextFormat(color=TextColors.RED, bold=True)
            )
        )}")


@app.command()
def set_device(
    port: str,
    address: int,
    config_type: str,
    baudrate: int = 9600,
    parity: str = "N",
    stopbits: int = 1,
    timeout: float = 1.0,
):
    """Selects the Modbus configuration for both modes of operation. config_type can be 'master' or 'slave'"""
    match config_type:
        case "master":
            config_type = DeviceConfigType.master
        case "slave":
            config_type = DeviceConfigType.slave
        case _:
            print(f"{format_text_element(
                TextElement(
                    value="Invalid config type. Use 'master' or 'slave'.",
                    format=TextFormat(color=TextColors.RED, bold=True)
                )
            )}")
    config = DeviceConfig(
        port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, timeout=timeout
    )
    initialize_device(
        config.port, config.baudrate, config.parity, config.stopbits, config.timeout
    )
    set_device_config(port, address, baudrate, parity, stopbits, timeout, config_type)


@app.command()
def show_config(config_type: str):
    """Shows the current device configuration. config_type can be 'master' or 'slave'"""
    match config_type:
        case "master":
            config_type = DeviceConfigType.master
        case "slave":
            config_type = DeviceConfigType.slave
        case _:
            print(f"{format_text_element(
                TextElement(
                    value="Invalid config type. Use 'master' or 'slave'.",
                    format=TextFormat(color=TextColors.RED, bold=True)
                )
            )}")

    table = get_device_config(config_type)
    console.print(table)
