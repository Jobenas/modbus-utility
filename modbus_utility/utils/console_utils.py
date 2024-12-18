from pydantic import BaseModel
from rich.table import Table


class TextColors:
	"""
	Represents a set of text colors
	"""
	BLACK = "black"
	RED = "red"
	GREEN = "green"
	YELLOW = "yellow"
	BLUE = "blue"
	MAGENTA = "magenta"
	CYAN = "cyan"
	WHITE = "white"


class TextFormat(BaseModel):
	"""
	Represents a text format
	"""
	bold: bool = False
	color: str | None = None


class TextElement(BaseModel):
	"""
	Represents an element in a row of a table
	"""
	value: str | int | float | bytes
	format: TextFormat | None = None


def format_text_element(element: TextElement) -> str:
	"""
	Formats a table element for display
	:param element: Element to format
	:return: Formatted element
	"""
	color_str = ''
	if element.format:
		color_str = f"[{f'{'bold' if element.format.bold else ''} ' if element.format else ''}{element.format.color}]"
	return f"{color_str if element.format else ''}{element.value}"


def generate_table(columns: list[str], rows: list[list[TextElement]]) -> Table:
	"""
	Generates a table with the specified contents
	:param columns: Name of the column headers to use in the table
	:param rows: List of rows to add to the table
	:return:
	"""
	table = Table(*[format_text_element(column) for column in columns])
	for row in rows:
		row_element_str = [
			format_text_element(row_element) for row_element in row
		]
		table.add_row(*row_element_str)

	return table