# modbus_serial.py
import serial
import logging
import serial.tools.list_ports

device_address = None


def initialize_device(port: str, baudrate: int, parity: str, stopbits: int, timeout: float) -> serial.Serial:
    ser = serial.Serial(
        port=port,
        baudrate=baudrate,
        parity=parity,
        stopbits=stopbits,
        timeout=timeout
    )
    logging.info(f"Initialized device on port {port}")

    return ser


def calculate_crc(data: bytes) -> int:
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 0x0001) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc


def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return ports
