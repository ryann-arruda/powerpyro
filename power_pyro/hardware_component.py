from abc import ABC, abstractmethod
from os_type import OsType

class HardwareComponent(ABC):
    def __init__(self, operating_system: OsType):
        self.__name:str
        self.__total_energy_consumed:float = 0.0
        self.__operating_system: OsType = operating_system
    
    def get_name(self) -> str:
        return self.__name

    def get_total_energy_consumed(self) -> float:
        return self.__total_energy_consumed

    def get_operating_system(self) -> OsType:
        return self.__operating_system
    
    def update_energy_consumed(self, energy_consumed_per_time: float) -> None:
        self.__total_energy_consumed += energy_consumed_per_time

    @abstractmethod
    def get_power(self) -> float:
        pass