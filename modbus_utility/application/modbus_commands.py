# modbus_commands.py
import json
import logging
import os
import struct
import time

from pydantic import BaseModel, conint
from rich import print
from rich.console import Console
from rich.table import Table
import serial
import typer
from typing import Optional

from modbus_utility.physical.modbus_serial import initialize_device, calculate_crc, list_serial_ports


SESSION_FILE = "modbus_session.json"

console = Console()


# Define configuration model for device parameters
class DeviceConfig(BaseModel):
    port: str
    baudrate: conint(gt=0) = 9600
    parity: str = 'N'
    stopbits: conint(gt=0, lt=3) = 1
    timeout: Optional[float] = 1.0


def save_session(data):
    with open(SESSION_FILE, 'w') as f:
        json.dump(data, f)


def load_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    return None


def select_device(port: str, address: int, baudrate: int = 9600, parity: str = 'N', stopbits: int = 1, timeout: float = 1.0):
    """Select the MODBUS device to interact with."""
    config = DeviceConfig(port=port, baudrate=baudrate, parity=parity, stopbits=stopbits, timeout=timeout)
    initialize_device(config.port, config.baudrate, config.parity, config.stopbits, config.timeout)
    session_data = {
        "port": port,
        "address": address,
        "baudrate": baudrate,
        "parity": parity,
        "stopbits": stopbits,
        "timeout": timeout
    }
    save_session(session_data)
    print(f"Selected device at address {address} on port {port}")


def read_register(
        register: int,
        num_registers: int = 1,
        show_frame_info: bool = False
):
    """Read register(s) from the selected MODBUS device."""
    session = load_session()
    if session is None:
        print("No device selected. Use 'select-device' first.")
        raise typer.Exit()

    address = session["address"]

    try:
        ser = initialize_device(
            session["port"],
            session["baudrate"],
            session["parity"],
            session["stopbits"],
            session["timeout"]
        )
    except serial.SerialException:
        print("Failed to initialize serial device")
        raise typer.Exit()

    try:
        # Construct Modbus request
        function_code = 3  # Read holding registers
        request = struct.pack('>B B H H', address, function_code, register, num_registers)
        crc = struct.pack('<H', calculate_crc(request))
        request += crc

        if show_frame_info:
            print(f"[!] Request frame: [bold green]{request}")
        # Send request
        ser.write(request)
        time.sleep(0.1)

        # Read response
        response = ser.read(5 + 2 * num_registers)
        if show_frame_info:
            print(f"[!] Response frame: [bold green]{response}")

        if response[1] & 0x80:
            raise Exception(f"Error response received: {response[2]}")

        if len(response) < 5 + 2 * num_registers:
            raise Exception("Incomplete response received")

        # Parse response
        _, recv_function_code, byte_count = struct.unpack('>B B B', response[:3])
        if recv_function_code != function_code:
            raise Exception(f"Invalid function code received: {recv_function_code}")

        values = struct.unpack(f'>{num_registers}H', response[3:3 + 2 * num_registers])
        table = Table("[bold blue]REGISTER", "[bold green]VALUE")
        for i, value in enumerate(values):
            table.add_row(f"[bold blue]{register + i}", f"[bold green]{value}")
        console.print(table)
        # print(f"Register {register}: {values}")
        logging.info(f"Read register {register} with value: {values}")
    except Exception as e:
        print(f"[bold white]Failed to read register {register}: [bold red]{e}")
        logging.error(f"Failed to read register {register}: {e}")


def write_register(register: int, value: int):
    """Write value to a register of the selected MODBUS device."""
    session = load_session()
    if session is None:
        print("No device selected. Use 'select-device' first.")
        raise typer.Exit()

    address = session["address"]

    try:
        ser = initialize_device(
            session["port"],
            session["baudrate"],
            session["parity"],
            session["stopbits"],
            session["timeout"]
        )
    except serial.SerialException:
        print("Failed to initialize serial device")
        raise typer.Exit()

    try:
        # Construct Modbus request
        function_code = 6  # Write single register
        request = struct.pack('>B B H H', address, function_code, register, value)
        crc = struct.pack('<H', calculate_crc(request))
        request += crc

        # Send request
        ser.write(request)
        time.sleep(0.1)

        # Read response
        response = ser.read(8)
        if len(response) < 8:
            raise Exception("Incomplete response received")

        # Parse response
        _, recv_function_code, recv_register, recv_value = struct.unpack('>B B H H', response[:7])
        if recv_function_code != function_code or recv_register != register or recv_value != value:
            raise Exception("Invalid response received")

        print(f"Wrote value {value} to register {register}")
        logging.info(f"Wrote value {value} to register {register}")
    except Exception as e:
        print(f"Failed to write to register {register}: {e}")
        logging.error(f"Failed to write to register {register}: {e}")


def list_ports():
    """List all available serial ports."""
    ports = list_serial_ports()
    if ports:
        print("[bold magenta]Available serial ports:")
        table = Table("PORT", "DESCRIPTION")
        for port in ports:
            # print(f"- [bold blue]{port.device} [white]- [bold green]{port.description}")
            table.add_row(f"[bold blue]{port.device}", f"[bold green]{port.description}")

        console.print(table)
    else:
        print("[bold red]No serial ports found.")


def info():
    """List the software's version information"""
    print("[bold blue]Modbus Utility v0.1")
    print("[bold green]Developed by EAT Team")
