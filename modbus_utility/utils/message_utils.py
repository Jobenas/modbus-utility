import struct

from modbus_utility.physical.modbus_serial import calculate_crc


def pack_message(addr: int, func_code: int, register: int, num_registers: int, big_endian: bool =True) -> bytes:
	"""
	Packs the relevant information as a modbus message with the correct format.
	:param addr: Address of the modbus device to send the message to.
	:param func_code: Function code of the message.
	:param register: Starting register for the operation.
	:param num_registers: Number of registers to read/write.
	:param big_endian: Endianness of the message.
	:return: Packed message as bytes.
	"""
	format_str = f"{'>' if big_endian else '<'}B B H H"
	message = struct.pack(
		format_str, addr, func_code, register, num_registers
	)
	crc = struct.pack(f"{'<' if big_endian else '>'}H", calculate_crc(message))

	message += crc

	return message


def unpack_data(format_str: str, data: bytes) -> tuple:
	"""
	Unpacks the byte data using the provided format string and returns a tuple of data.
	:param format_str: Format string to use for unpacking the data.
	:param data: Data to unpack.
	:return: Tuple of unpacked data.
	"""

	return struct.unpack(format_str, data)