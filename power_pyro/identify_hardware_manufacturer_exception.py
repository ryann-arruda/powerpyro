from hardware_type import HardwareType

class IdentifyHardwareManufacturerException(Exception):
    """Exception raised when the hardware manufacturer cannot be identified.

    Args:
        hardware_type (HardwareType): The type of the hardware whose manufacturer could not be identified.
        msg (str): Descriptive error message (optional, default is "Unable to identify hardware manufacturer").
    """
    def __init__(self, hardware_type: HardwareType, msg: str = "Unable to identify hardware manufacturer"):
        super().__init__(hardware_type.name + ": " + msg)
