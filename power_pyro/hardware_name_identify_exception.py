from hardware_type import HardwareType

class HardwareNameIdentifyException(Exception):

    def __init__(self, hardware_type: HardwareType, msg: str = "Unable to identify hardware name"):
        super().__init__(hardware_type.name + ": " + msg)