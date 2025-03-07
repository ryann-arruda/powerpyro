from abc import ABC, abstractmethod

class HardwareComponent(ABC):
    def __init__(self):
        self.__name:str
        self.__total_energy_consumed:float
    
    def get_name(self) -> str:
        return self.__name

    def get_total_energy_consumed(self) -> float:
        return self.__total_energy_consumed
    
    def update_energy_consumed(self, energy_consumed_per_time: float) -> None:
        self.__total_energy_consumed += energy_consumed_per_time

    @abstractmethod
    def get_power(self) -> float:
        pass