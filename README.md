# MODBUS Utility CLI

This CLI tool is a utility to handle simple modbus operations. It is intended to work with ECM-P devices, but might expand to handle more operations down the road.

## installation

Navigate to the wheel file and run the following pip command

```bash
pip install modbus_utility-0.1.0-py3-none-any.whl
```

If working with poetry the option should be

```bash
poetry add modbus_utility-0.1.0-py3-none-any.whl
```

## Use

The CLI tool is intended to be used as follows:

```bash
modbus_utility --help
```
This displays all the options available on the tool.

## Version information.

The version of the tool can be checked by running the following command:

```bash
modbus_utility info
```