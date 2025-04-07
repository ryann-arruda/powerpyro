from hardware_component import HardwareComponent
from invalid_keys_error_exception import InvalidKeysErrorException
from hardware_component_factory import HardwareComponentFactory
from cpu_component_factory import CpuComponentFactory
from gpu_component_factory import GpuComponentFactory
from memory_component_factory import MemoryComponentFactory
from os_type import OsType

from typing import Dict
import time
import os
from threading import Thread

class Monitor():
    def __init__(self, required_components: Dict[str, bool]):
        self.__operating_system: OsType = self.__get_operating_system()
        self.__components: Dict[str, HardwareComponent] = self.__create_components(required_components)
        self.__total_energy_consumed: float
        self.__stop_sign: bool = False
        self.__thread:Thread = Thread(target=self.__monitor)
        self.__WATT_TO_KWH:float = 3_600_000
    
    def __get_operating_system(self) -> OsType:
        """Determines the operating system type.
        
        Returns: 
            The operating system type as OsType.

        Raises: 
            OSError: If the OS cannot be identified.
        """
        if os.name == 'nt':
            return OsType.WINDOWS
        elif os.name == 'posix':
            return OsType.LINUX
        else:
            raise OSError("Unable to identify operating system")

    def __check_components(self, required_components: Dict[str, bool]) -> bool:
        """Validates the required components keys.

        Args:
            required_components: Dictionary of required components.

        Returns: 
            bool:
                - 'True' if all the dictionary keys are in the list, 
                - 'False' otherwise.
        """
        required_keys = ['cpu', 'gpu', 'memory']

        return len(required_components.keys()) <= len(required_keys) and all(key in required_keys for key in required_components)
    
    def __create_components(self, required_components: Dict[str, bool]) -> Dict[str, HardwareComponent]:
        """Creates the required hardware components using the appropriate factories.

        Args:
            required_components: Dictionary indicating which components should be created.

        Returns: 
            components: Dictionary containing the created hardware components.

        Raises:
            InvalidKeysErrorException: If the required components contain invalid keys.
        """
        if not self.__check_components(required_components):
            raise InvalidKeysErrorException()

        factories: Dict[str, HardwareComponentFactory] = { 
            'cpu': CpuComponentFactory(),
            'gpu': GpuComponentFactory(),
            'memory': MemoryComponentFactory()
        }

        components: Dict[str, HardwareComponent] = {}
        
        for component in required_components:
            components[component] = factories[component].create_component(self.__operating_system)

            if hasattr(components[component], 'open'):
                components[component].open()
        
        return components
    
    def __close_resources(self) -> None:
        """Closes resources allocated by the components."""
        for component in self.__components:
            
            if hasattr(self.__components[component], 'close'):
                self.__components[component].close()
    
    def get_energy_consumed_by_components(self) -> Dict[str, float]:
        """Retrieves the total energy consumed by each hardware component.

        Returns: 
            energy_consumed_by_components: A dictionary where the keys are component names ('cpu', 'gpu', 'memory') and the values are the energy consumed by each component.
        """
        energy_consumed_by_components: Dict[str, float] = {}

        if 'cpu' in self.__components:
            energy_consumed_by_components['cpu'] = self.__components['cpu'].total_energy_consumed()

            if 'gpu' in self.__components:
                energy_consumed_by_components['gpu'] = self.__components['gpu'].total_energy_consumed()

                if 'memory' in self.__components:
                    energy_consumed_by_components['memory'] = self.__components['memory'].total_energy_consumed()
            
            if 'memory' in self.__components:
                energy_consumed_by_components['memory'] = self.__components['memory'].total_energy_consumed()
        
        return energy_consumed_by_components
    
    def get_total_energy_consumed(self) -> float:
        """Retrieves the total energy consumed by all components monitored."""
        return self.__total_energy_consumed

    def __monitor(self) -> None:
        """Monitors energy consumption of components at regular intervals."""

        while not self.__stop_sign:
            start = time.time() 

            time.sleep(10)
            
            end = time.time() 

            period = end - start

            if 'cpu' in self.__components: 
                cpu = self.__components['cpu']
                cpu.update_energy_consumed((cpu.get_power() * cpu.get_cpu_percent_for_process() * period)/self.__WATT_TO_KWH)

            if 'gpu' in self.__components:   
                gpu = self.__components['gpu']  
                gpu.update_energy_consumed((gpu.get_power() * period)/self.__WATT_TO_KWH)

            if 'memory' in self.__components:     
                memory = self.__components['memory']
                memory.update_energy_consumed((memory.get_power() * period)/self.__WATT_TO_KWH)
        
        if self.__operating_system == OsType.WINDOWS:
            self.__close_resources()
    
    def start(self) -> None:
        self.__thread.start()
    
    def end(self) -> None:
        self.__stop_sign = True
        self.__thread.join()