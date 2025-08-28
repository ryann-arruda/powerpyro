from .hardware_component import HardwareComponent
from .os_type import OsType

from abc import ABC, abstractmethod

class HardwareComponentFactory(ABC):
    """Abstract base class representing a factory for creating hardware components.
    
    This class defines a factory pattern for creating concrete implementations of
    HardwareComponent based on the operating system.
    """
    def __init__(self):
        pass
    
    @abstractmethod
    def create_component(self, operating_system: OsType) -> HardwareComponent:
        pass
