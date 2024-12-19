import typer

from modbus_utility.utils.console_utils import (
    format_text_element,
    TextElement,
    TextFormat,
    TextColors,
)
from modbus_utility.utils.modbus_master import ModbusMaster
from modbus_utility.utils.operation_utils import load_session, DeviceConfigType

app = typer.Typer()


@app.command()
def write_register(register: int, value: int):
    """Write value to a register of the selected MODBUS device."""
    session = load_session(DeviceConfigType.master)
    if session is None:
        print(
            f"{format_text_element(
            TextElement(
                value="No device selected. Use 'select-device' first.",
                format=TextFormat(color=-TextColors.RED, bold=True)
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

    modbus_client.write_register(register, value)
