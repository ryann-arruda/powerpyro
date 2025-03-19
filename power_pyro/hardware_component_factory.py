from hardware_component import HardwareComponent

from abc import ABC, abstractmethod

class HardwareComponentFactory(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def create_component() -> HardwareComponent:
        pass