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
        if os.name == 'nt':
            return OsType.WINDOWS
        elif os.name == 'posix':
            return OsType.LINUX
        else:
            raise OSError("Unable to identify operating system")

    def __check_components(self, required_components: Dict[str, bool]) -> bool:
        required_keys = ['cpu', 'gpu', 'memory']

        return len(required_components.keys()) <= len(required_keys) and all(key in required_keys for key in required_components)
    
    def __create_components(self, required_components: Dict[str, bool]) -> Dict[str, HardwareComponent]:
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
        for component in self.__components:
            
            if hasattr(self.__components[component], 'close'):
                self.__components[component].close()
    
    def get_total_energy_consumed(self) -> float:
        return self.__total_energy_consumed

    def __monitor(self) -> None:

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