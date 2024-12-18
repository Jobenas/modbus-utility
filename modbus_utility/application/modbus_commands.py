# modbus_commands.py
import logging
import struct
import time

from rich import print
from rich.console import Console
import serial
import typer

from modbus_utility.physical.modbus_serial import (
    initialize_device,
    calculate_crc,
    list_serial_ports,
)
from modbus_utility.utils.console_utils import generate_table, TextElement, TextFormat, TextColors, format_text_element
from modbus_utility.utils.message_utils import pack_message
from modbus_utility.utils.modbus_client import ModbusClient
from modbus_utility.utils.operation_utils import DeviceConfig, save_session, DeviceConfigType, load_session

console = Console()


def select_device(
    port: str,
    address: int,
    baudrate: int = 9600,
    parity: str = "N",
    stopbits: int = 1,
    timeout: float = 1.0,
):
    """Select the MODBUS device to interact with."""
    config = DeviceConfig(
        port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, timeout=timeout
    )
    initialize_device(
        config.port, config.baudrate, config.parity, config.stopbits, config.timeout
    )
    session_data = {
        "port": port,
        "address": address,
        "baudrate": baudrate,
        "parity": parity,
        "stopbits": stopbits,
        "timeout": timeout,
    }
    save_session(session_data, DeviceConfigType.master)
    print(f"Selected device at address {address} on port {port}")


def read_register(
    register: int,
    num_registers: int = 1,
    show_frame_info: bool = False,
    display_hex: bool = True,
):
    """Read register(s) from the selected MODBUS device."""
    session = load_session(DeviceConfigType.master)
    if session is None:
        print(f"{format_text_element(
            TextElement(
                value="No device selected. Use 'select-device' first.",
                format=TextFormat(color=TextColors.RED, bold=True)
            )
        )}")
        raise typer.Exit()

    address = session["address"]

    try:
        ser = initialize_device(
            session["port"],
            session["baudrate"],
            session["parity"],
            session["stopbits"],
            session["timeout"],
        )
    except serial.SerialException:
        print("Failed to initialize serial device")
        raise typer.Exit()

    try:
        # Construct Modbus request
        function_code = 3  # Read holding registers
        request = pack_message(address, function_code, register, num_registers)
        if show_frame_info:
            print(f"[!] Request frame: {format_text_element(TextElement(value=request, format=TextFormat(color=TextColors.GREEN, bold=True)))}")
        # Send request
        ser.write(request)
        time.sleep(0.1)

        # Read response
        response = ser.read(5 + 2 * num_registers)
        if show_frame_info:
            print(
                f"[!] Response frame: "
                f"{format_text_element(
                    TextElement(
                        value=response, 
                        format=TextFormat(
                            color=TextColors.GREEN, 
                            bold=True
                        )
                    )
                )}")

        if response[1] & 0x80:
            raise Exception(f"Error response received: {response[2]}")

        if len(response) < 5 + 2 * num_registers:
            raise Exception("Incomplete response received")

        # Parse response
        _, recv_function_code, byte_count = struct.unpack(">B B B", response[:3])
        if recv_function_code != function_code:
            raise Exception(f"Invalid function code received: {recv_function_code}")

        values = struct.unpack(
            f">{num_registers}H", response[3 : 3 + 2 * num_registers]
        )
        table = generate_table(
            [
                TextElement(value="REGISTER", format=TextFormat(color=TextColors.BLUE, bold=True)),
                TextElement(value="VALUE", format=TextFormat(color=TextColors.GREEN, bold=True)),
            ],
            [
                [
                    TextElement(value=register + i, format="bold blue"),
                    TextElement(value=value if not display_hex else hex(value), format="bold green"),
                ]
                for i, value in enumerate(values)
            ],
        )
        console.print(table)
        # print(f"Register {register}: {values}")
        logging.info(f"Read register {register} with value: {values}")
    except Exception as e:
        print(f""
              f"{format_text_element(TextElement(
                  value=f'Failed to read register {register}: ', 
                  format=TextFormat(color=TextColors.WHITE, bold=True)))}"
              f"{format_text_element(TextElement(value=f'{e}', format=TextFormat(color=TextColors.RED, bold=True)))}")
        logging.error(f"Failed to read register {register}: {e}")


def write_register(register: int, value: int):
    """Write value to a register of the selected MODBUS device."""
    session = load_session(DeviceConfigType.master)
    if session is None:
        print(f"{format_text_element(
            TextElement(
                value="No device selected. Use 'select-device' first.",
                format=TextFormat(color=TextColors.RED, bold=True)
            )
        )}")
        raise typer.Exit()

    modbus_client = ModbusClient(
        port=session["port"],
        baudrate=session["baudrate"],
        parity=session["parity"],
        stop_bits=session["stopbits"],
        timeout=session["timeout"],
        slave_address=session["address"],
    )

    modbus_client.write_register(register, value)


def list_ports():
    """List all available serial ports."""
    ports = list_serial_ports()
    if ports:
        print("[bold magenta]Available serial ports:")

        table = generate_table(
            [
                TextElement(value="PORT"),
                TextElement(value="DESCRIPTION")
            ],
            [
                [
                    TextElement(value=port.device, format=TextFormat(color=TextColors.BLUE, bold=True)),
                    TextElement(value=port.description, format=TextFormat(color=TextColors.GREEN, bold=True))
                ]
                for port in ports
            ]
        )

        console.print(table)
    else:
        print(f"{format_text_element(TextElement(
            value="No serial ports found.",
            format=TextFormat(color=TextColors.RED, bold=True)))}")


def info():
    """List the software's version information"""
    print("[bold blue]Modbus Utility v0.1.1")
    print("[bold green]Developed by EAT Team")
