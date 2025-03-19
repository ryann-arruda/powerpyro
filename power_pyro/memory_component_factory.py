from hardware_component_factory import HardwareComponentFactory
from hardware_component import HardwareComponent
from memory import Memory

class MemoryComponentFactory(HardwareComponentFactory):
    
    def __init__(self):
        super().__init__()

    def create_component(self) -> HardwareComponent:
        return Memory()