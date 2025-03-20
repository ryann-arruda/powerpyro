from hardware_component_factory import HardwareComponentFactory
from os_type import OsType
from hardware_component import HardwareComponent
from memory import Memory

class MemoryComponentFactory(HardwareComponentFactory):
    
    def __init__(self):
        super().__init__()

    def create_component(self, operating_system: OsType) -> HardwareComponent:
        return Memory(operating_system)