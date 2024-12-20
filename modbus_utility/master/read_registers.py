import logging

from rich.console import Console
import typer

from modbus_utility.utils.console_utils import (
    format_text_element,
    TextElement,
    TextFormat,
    TextColors,
    generate_table,
)
from modbus_utility.utils.modbus_master import ModbusMaster
from modbus_utility.utils.operation_utils import load_session, DeviceConfigType

app = typer.Typer()

console = Console()


@app.command()
def read_register(
    register: int,
    num_registers: int = 1,
    show_frame_info: bool = False,
    display_hex: bool = True,
):
    """Read register(s) from the selected MODBUS device."""
    session = load_session(DeviceConfigType.master)
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

    modbus_client = ModbusMaster(
        port=session["port"],
        baudrate=session["baudrate"],
        parity=session["parity"],
        stop_bits=session["stopbits"],
        timeout=session["timeout"],
        slave_address=session["address"],
    )
    values = modbus_client.read_holding_register(
        register, num_registers, show_frame_info
    )

    table = generate_table(
        [
            TextElement(
                value="REGISTER", format=TextFormat(color=TextColors.BLUE, bold=True)
            ),
            TextElement(
                value="VALUE", format=TextFormat(color=TextColors.GREEN, bold=True)
            ),
        ],
        [
            [
                TextElement(
                    value=register + i,
                    format=TextFormat(color=TextColors.BLUE, bold=True),
                ),
                TextElement(
                    value=value if not display_hex else hex(value),
                    format=TextFormat(color=TextColors.GREEN, bold=True),
                ),
            ]
            for i, value in enumerate(values)
        ],
    )
    console.print(table)
    logging.info(f"Read register {register} with value: {values}")
