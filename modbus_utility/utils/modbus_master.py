import logging
import struct
import time

import serial
import typer

from modbus_utility.physical.modbus_serial import initialize_device
from modbus_utility.utils.console_utils import (
    format_text_element,
    TextElement,
    TextFormat,
    TextColors,
)
from modbus_utility.utils.message_utils import pack_message


class ModbusMaster:
    def __init__(
        self,
        port: str,
        baudrate: int,
        parity: str,
        stop_bits: int,
        timeout: float,
        slave_address: int,
    ):
        """
        Creates a ModbusMaster object
        :param port: Serial port to connect to
        :param baudrate: Baud rate to use in the communication
        :param parity: Parity to use in the communication
        :param stop_bits: Number of stop bits to use in the communication
        :param timeout: Timeout for the communication
        :param slave_address: Address of the slave device
        """
        try:
            self.ser = initialize_device(port, baudrate, parity, stop_bits, timeout)
        except serial.SerialException:
            print(f"{format_text_element(
				TextElement(
					value="Failed to initialize serial device", 
					format=TextFormat(color=TextColors.RED,bold=True)
				)
			)}")
            logging.error("Failed to initialize serial device")
            raise typer.exit()

        self.slave_address = slave_address

    def send_request(self, request: bytes):
        """
        Sends a request message to a modbus slave device, and generates a delay.
        :param request: Request message to send as a byte stream
        :return: None.
        """
        try:
            self.ser.write(request)
        except serial.SerialException:
            print(
                f"{format_text_element(TextElement(value='Failed to send request.', format=TextFormat(color=TextColors.RED, bold=False)))}"
            )
            logging.error("Failed to write to the serial port")
            raise typer.Exit()
        time.sleep(0.1)

    def read_response(self, num_bytes: int) -> bytes:
        """
        Reads a response message from a modbus slave device.
        :param num_bytes: Number of bytes to read from the bus
        :return: Response message as a byte stream
        """
        try:
            response = self.ser.read(num_bytes)
        except serial.SerialException:
            print(
                f"{format_text_element(TextElement(value='Failed to read from the slave.', format=TextFormat(color=TextColors.RED, bold=False)))}"
            )
            logging.error("Failed to read from the serial port")
            raise typer.Exit()
        return response

    @staticmethod
    def extract_write_response(response_bytes: bytes) -> tuple[int, int, int]:
        """
        Extracts the function code, register and value from a write response.
        :param response_bytes: Response bytes to extract the data from
        :return: Tuple of function code, register and value
        """
        _, function_code, register, value = struct.unpack(
            ">B B H H", response_bytes[:5]
        )
        return function_code, register, value

    @staticmethod
    def extract_holding_register_response(
        response_bytes: bytes,
        num_registers: int,
        expected_function_code: int,
        big_endian: bool = True,
    ) -> tuple[int]:
        """
        Extracts the function code, byte count, register and values from a holding register response.
        :param response_bytes: Response bytes to extract the data from.
        :param num_registers: Number of registers that have been read.
        :param expected_function_code: Expected function code in the response.
        :param big_endian: Endianness of the response, True for big-endian.
        :return: Tuple of read values.
        """
        _, recv_function_code, byte_count = struct.unpack(">B B B", response_bytes[:3])
        if recv_function_code != expected_function_code:
            raise Exception(
                f"Invalid function code received: {format_text_element(
					TextElement(
						value=recv_function_code,
						format=TextFormat(
							color=TextColors.RED,
							bold=True
						)
					)
				)}"
            )
        reg_start = 3
        reg_end = reg_start + byte_count
        values = struct.unpack(
            f"{'> ' if big_endian else '<'}{num_registers}H",
            response_bytes[reg_start:reg_end],
        )

        return values

    @staticmethod
    def verify_write_response(
        recv_function_code: int,
        recv_register: int,
        recv_value: int,
        function_code: int,
        register: int,
        value: int,
    ) -> bool:
        """
        Verifies the response received after writing to a register is correct.
        :param recv_function_code: Received function code
        :param recv_register: Received register
        :param recv_value: Received value
        :param function_code: Function code of the request.
        :param register: Register that was written to.
        :param value: Value that was written to the register.
        :return: True if the response is correct, False otherwise
        """
        if (
            recv_function_code != function_code
            or recv_register != register
            or recv_value != value
        ):
            return False

        return True

    def write_register(self, register: int, value: int) -> None:
        """
        Writes a value to a register on a modbus slave device.
        :param register: Register to write to
        :param value: Value to write to the register
        :return: None
        """
        try:
            function_code = 6
            request = pack_message(self.slave_address, function_code, register, value)

            self.send_request(request)

            response = self.read_response(8)
            if len(response) < 8:
                raise Exception("Incomplete response received")

            recv_function_code, recv_register, recv_value = self.extract_write_response(
                response
            )

            if not self.verify_write_response(
                recv_function_code,
                recv_register,
                recv_value,
                function_code,
                register,
                value,
            ):
                raise Exception("Incomplete response received")

            print(
                f"Wrote value {format_text_element(
				TextElement(
					value=value,
					format=TextFormat(
						color=TextColors.GREEN,
						bold=True
					)
				)
			)} to register {format_text_element(
				TextElement(
					value=register,
					format=TextFormat(
						color=TextColors.MAGENTA,
						bold=True
					)
				)
			)}"
            )
            logging.info(f"Wrote value {value} to register {register}")
        except serial.SerialException:
            print(
                f"{format_text_element(
				TextElement(
					value="Failed to write to register. Check the connection and try again.",
					format=TextFormat(
						color=TextColors.RED,
						bold=True
					)
				)
			)}"
            )
            logging.error(
                f"Failed to write to register {register} - Exception: {serial.SerialException}"
            )

    def read_holding_register(
        self, start_reg: int, num_reg: int, show_frame_info: bool
    ) -> tuple[int]:
        """
        Reads a group of holding registers (function code 3) from the modbus slave.
        :param start_reg: Starting register to read from.
        :param num_reg: Number of registers to read.
        :param show_frame_info: Flag to indicate if the raw frames being transferred should be displayed.
        :return: Tuple of register values ordered from the starting register.
        """
        function_code = 3
        request = pack_message(self.slave_address, function_code, start_reg, num_reg)

        if show_frame_info:
            print(
                f"[!] Request frame: {format_text_element(TextElement(value=request, format=TextFormat(color=TextColors.GREEN, bold=True)))}"
            )

        self.send_request(request)

        response = self.read_response(5 + 2 * num_reg)

        if show_frame_info:
            print(
                f"[!] Response frame: {format_text_element(
					TextElement(
						value=response, 
						format=TextFormat(color=TextColors.GREEN, bold=True)
					)
				)}"
            )

        if response[1] & 0x80:
            raise Exception(f"Error response received: {response[2]}")

        if len(response) < 5 + 2 * num_reg:
            raise Exception("Incomplete response received")

        values = self.extract_holding_register_response(
            response, num_reg, function_code
        )

        return values
