from hardware_component_factory import HardwareComponentFactory
from hardware_component import HardwareComponent
from cpu import Cpu

class CpuComponentFactory(HardwareComponentFactory):
    
    def __init__(self):
        super().__init__()

    def create_component(self) -> HardwareComponent:
        return Cpu()