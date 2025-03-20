from hardware_component import HardwareComponent
from os_type import OsType

from abc import ABC, abstractmethod

class HardwareComponentFactory(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def create_component(self, operating_system: OsType) -> HardwareComponent:
        pass