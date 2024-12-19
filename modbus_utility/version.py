import typer

from modbus_utility.utils.console_utils import (
    format_text_element,
    TextElement,
    TextFormat,
    TextColors,
)

app = typer.Typer()


@app.command()
def version():
    """List the software's version information"""
    print(
        format_text_element(
            TextElement(
                value="Modbus Utility v0.2.0",
                format=TextFormat(color=TextColors.BLUE, bold=True),
            )
        )
    )
    print(
        format_text_element(
            TextElement(
                value="Developed by EAT Team",
                format=TextFormat(color=TextColors.GREEN, bold=True),
            )
        )
    )
