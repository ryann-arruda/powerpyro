from hardware_type import HardwareType

class IdentifyHardwareManufacturerException(Exception):

    def __init__(self, hardware_type: HardwareType, msg: str = "Unable to identify hardware manufacturer"):
        super().__init__(hardware_type.name + ": " + msg)