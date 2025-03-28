from hardware_component_factory import HardwareComponentFactory
from os_type import OsType
from hardware_component import HardwareComponent
from cpu import Cpu

class CpuComponentFactory(HardwareComponentFactory):
    """Factory class for creating CPU components.
    
    This class implements the 'HardwareComponentFactory' to provide concrete CPU components
    based on the specified operating system.
    """
    def __init__(self):
        super().__init__()

    def create_component(self, operating_system: OsType) -> HardwareComponent:
        return Cpu(operating_system)
