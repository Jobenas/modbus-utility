import logging
import time

from rich.console import Console
import serial
import typer

from modbus_utility.physical.modbus_serial import initialize_device, calculate_crc

from modbus_utility.utils.console_utils import format_text_element, TextElement, TextFormat, TextColors


console = Console()


class ModbusSlave:
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
		Creates a ModbusSlave object.
		:param port: Serial port to connect to
		:param baudrate: Baud rate to use in the communication
		:param parity: Parity to use in the communication
		:param stop_bits: Number of stop bits to use in the communication
		:param timeout: Timeout for the communication
		:param slave_address: Modbus slave address this object will bind to
		"""
		try:
			self.ser = initialize_device(port, baudrate, parity, stop_bits, timeout)
		except serial.SerialException:
			console.print(f"{format_text_element(
				TextElement(
					value="Failed to initialize serial device", 
					format=TextFormat(color=TextColors.RED,bold=True)
				)
			)}")
			logging.error("Failed to initialize serial device")
			raise typer.Exit()

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
			console.print(
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
			console.print(
				f"{format_text_element(TextElement(value='Failed to read from the slave.', format=TextFormat(color=TextColors.RED, bold=False)))}"
			)
			logging.error("Failed to read from the serial port")
			raise typer.Exit()
		return response

	def start_listening(
		self,
		show_debug: bool
	) -> None:
		"""
		Starts to listen for incoming data in the previously configured serial port.
		:param show_debug: Show debug information.
		:return:
		"""
		console.print(f"Listening for incoming data, "
			  f"to stop use {format_text_element(
				  TextElement(value="ctl + c", format=TextFormat(color=TextColors.CYAN, bold=True)))} "
			  f"or press {format_text_element(
				  TextElement(value="q", format=TextFormat(color=TextColors.CYAN, bold=True)))}")

		rx_buffer = b''
		while True:
			try:
				data = self.ser.read(100)
				if data:
					console.print(data)
					if len(data) < 6:
						continue
					if data[0] == self.slave_address:
						function_code = data[1]
						if function_code == 3:
							register = (data[2] << 8) + data[3]
							num_registers = (data[4] << 8) + data[5]
							crc = (data[-1] << 8) + data[-2]
							if crc == calculate_crc(data[:-2]):
								console.print(f"We have a request for reading {format_text_element(TextElement(value=num_registers, format=TextFormat(color=TextColors.CYAN)))} "
									  f"registers starting from register {format_text_element(TextElement(value=register, format=TextFormat(color=TextColors.CYAN)))}")
								response = b'\x01\x03\x04\x45\xea\x32\x00\xdb\xab'
								self.ser.write(response)
							else:
								console.print(f"{format_text_element(TextElement(value='CRC Error', format=TextFormat(color=TextColors.RED, bold=True)))}")
						else:
							console.print(f"{format_text_element(TextElement(value='Function code not supported.', format=TextFormat(color=TextColors.RED, bold=True)))}")
					else:
							console.print(
							f"{format_text_element(TextElement(value='Slave address does not match', format=TextFormat(color=TextColors.RED, bold=True)))}")

			except KeyboardInterrupt:
				console.print(f"{format_text_element(TextElement(value="Detected keyboard interrupt, exiting", format=TextFormat(color=TextColors.YELLOW, bold=True)))}")
				raise typer.Exit()

	def analyze_incoming_data(self, data_frame: bytes, show_debug: bool = False) -> tuple[bool, bytes]:
		"""
		Checks the data frame to see if it matches any modbus pattern.
		:param data_frame: Data frame to analyze as bytes.
		:param show_debug: Show debug information.
		return: a tuple containing a boolean indicating if the data frame is valid and the response to send if applies.
		"""
		recv_address = data_frame[0]
		if recv_address != self.slave_address:
			if show_debug:
				console.print(f"{format_text_element(
					TextElement(
						value='Received data from an unknown address.', 
						format=TextFormat(color=TextColors.RED, bold=True)
					)
				)}")
			return False, b''

		recv_func_code = data_frame[1]

		match recv_func_code:
			case 3:
				...
			case 4:
				...
			case 6:
				...
			case _:
				if show_debug:
					print(f"{format_text_element(
						TextElement(
							value='Unknown function code received.', 
							format=TextFormat(color=TextColors.RED, bold=True)
						)
					)}")
				return False, b''