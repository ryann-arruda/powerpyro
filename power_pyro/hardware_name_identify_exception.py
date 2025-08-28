from .hardware_type import HardwareType

class HardwareNameIdentifyException(Exception):
    """Exception raised when the hardware name cannot be identified.

    Args:
        hardware_type (HardwareType): The type of the hardware that could
        not be identified.
        msg (str): Descriptive error 
        message (optional, default is "Unable to identify hardware name").
    """
    def __init__(self, hardware_type: HardwareType, msg: str = "Unable to identify hardware name"):
        super().__init__(hardware_type.name + ": " + msg)