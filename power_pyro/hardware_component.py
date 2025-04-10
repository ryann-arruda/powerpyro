from os_type import OsType

from abc import ABC, abstractmethod

class HardwareComponent(ABC):
    """Abstract base class representing a hardware component.

    Attributes:
        __total_energy_consumed (float): Total energy consumed by the hardware
                                         component.
        __operating_system (OsType): The operating system where the hardware 
                                     component is running.
    """
    def __init__(self, operating_system: OsType):
        self.__total_energy_consumed: float = 0.0
        self.__operating_system: OsType = operating_system

    @property
    def total_energy_consumed(self) -> float:
        """Retrieves the total energy consumed by the hardware component.

        Returns:
            float: Total energy consumed.
        """
        return self.__total_energy_consumed

    @property
    def operating_system(self) -> OsType:
        """Retrieves the operating system of the hardware component.

        Returns:
            OsType: The operating system.
        """
        return self.__operating_system
    
    def update_energy_consumed(self, energy_consumed_per_time: float) -> None:
        """Updates the total energy consumed by adding the energy consumed
           over a period of time.

        Args:
            energy_consumed_per_time (float): The energy consumed during a 
            specific time interval.
        """
        self.__total_energy_consumed += energy_consumed_per_time

    @abstractmethod
    def get_power(self) -> float:
        """Abstract method to retrieve the power consumption of the hardware
           component.

        Returns:
            float: Power consumption in watts.
        """
        pass