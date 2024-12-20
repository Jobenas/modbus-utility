import json
import os
from typing import Optional

from pydantic import BaseModel, conint


# Define configuration model for device parameters
class DeviceConfig(BaseModel):
    port: str
    baudrate: conint(gt=0) = 9600
    parity: str = "N"
    stopbits: conint(gt=0, lt=3) = 1
    timeout: Optional[float] = 1.0


class DeviceConfigType:
    master = "modbus_session_master.json"
    slave = "modbus_session_slave.json"


def save_session(
    data: dict, session_type: DeviceConfigType = DeviceConfigType.master
) -> None:
    """
    Saves the device configuration to a session file.
    :param data: dictionary containing all the device configuration information
    :param session_type: type of device configuration
    :return: None
    """
    with open(session_type, "w") as f:
        json.dump(data, f)


def load_session(
    session_type: DeviceConfigType = DeviceConfigType.master,
) -> dict | None:
    """
    Loads the device configuration from a session file.
    :param session_type: type of device configuration
    :return: dictionary containing all the device configuration information if it exists else None
    """
    if os.path.exists(session_type):
        with open(session_type, "r") as f:
            return json.load(f)
    return None
