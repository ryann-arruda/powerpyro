from .hardware_component import HardwareComponent
from .invalid_keys_error_exception import InvalidKeysErrorException
from .hardware_component_factory import HardwareComponentFactory
from .cpu_component_factory import CpuComponentFactory
from .gpu_component_factory import GpuComponentFactory
from .memory_component_factory import MemoryComponentFactory
from .os_type import OsType

from typing import Dict, Any
import time
import os
from threading import Thread

class Monitor():
    """
    Class responsible for monitoring the energy consumption of 
    selected hardware components 
    (CPU, GPU, and memory) in a system.

    Attributes:
        __operating_system (OsType): The current operating system.
        __components (Dict[str, HardwareComponent]): Dictionary of initialized 
        hardware components.
        __stop_sign (bool): Flag to stop the monitoring loop.
        __thread (Thread): Thread in which monitoring occurs.
        __WATT_TO_KWH (float): Constant to convert energy from 
        watts to kilowatt-hours.
    """
    def __init__(self, required_components: Dict[str, bool]):
        """
        Initializes the Monitor class by setting up the operating system, 
        validating required components, creating component instances,
        and preparing the monitoring thread.

        Args:
            required_components (Dict[str, bool]): Dictionary specifying which 
            components ('cpu', 'gpu', 'memory') should be monitored.
        
        Raises:
            InvalidKeysErrorException: If any invalid keys are found in 
            the provided dictionary.

        Example:
            Basic usage monitoring only CPU:

            ```python
            from power_pyro import Monitor

            monitor = Monitor({'cpu': True, 'gpu': False, 'memory': False})
            ```

            Monitoring CPU and GPU:

            ```python
            from power_pyro import Monitor

            monitor = Monitor({'cpu': True, 'gpu': True, 'memory': False})
            ```

            Monitoring all components:

            ```python
            from power_pyro import Monitor

            monitor = Monitor({'cpu': True, 'gpu': True, 'memory': True})
            ```
        """
        self.__operating_system: OsType = self.__get_operating_system()
        self.__components: Dict[str, HardwareComponent] = self.__create_components(required_components)
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
    
    def get_monitored_components(self) -> Dict[str, Any]:
        """Retrieves the components to be monitored.
        
        Returns: 
            A dictionary with the monitoring status of the components 
            and the components themselves.

        Example:
            Example retrieving monitored components:

            ```python
            from power_pyro import Monitor

            # Monitor only CPU and GPU
            monitor = Monitor({'cpu': True, 'gpu': True, 'memory': False})
            components = monitor.get_monitored_components()

            print(components)
            # Output: {'cpu': True, 'gpu': True, 'memory': False}
            ```
        """
        monitored_components:Dict[str, Any] = {'cpu': {'component': None, 'monitored': False}, 
                                               'gpu': {'component': None, 'monitored': False}, 
                                               'memory': {'component': None, 'monitored': False}}

        for key in self.__components.keys():
            monitored_components[key]['component'] = self.__components[key]
            monitored_components[key]['monitored'] = True
        
        return monitored_components

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
            if required_components[component]:
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

        Example:
            ```python
            monitor = Monitor({'cpu': True, 'gpu': False})
            result = monitor.get_energy_consumed_by_components()
            print(result)  # {'cpu': 2.5}
            ```
        """
        energy_consumed_by_components: Dict[str, float] = {}

        if 'cpu' in self.__components:
            energy_consumed_by_components['cpu'] = self.__components['cpu'].total_energy_consumed

            if 'gpu' in self.__components:
                energy_consumed_by_components['gpu'] = self.__components['gpu'].total_energy_consumed

                if 'memory' in self.__components:
                    energy_consumed_by_components['memory'] = self.__components['memory'].total_energy_consumed
            
            if 'memory' in self.__components:
                energy_consumed_by_components['memory'] = self.__components['memory'].total_energy_consumed
        
        return energy_consumed_by_components
    
    def total_energy_consumed(self) -> float:
        """Retrieves the total energy consumed by all components monitored.
        
        Example:
            Get total energy consumption after monitoring:

            ```python
            from power_pyro import Monitor

            monitor = Monitor({'cpu': True, 'gpu': True, 'memory': False})
            monitor.start()
            # ... perform operations ...
            monitor.end()
            
            total_energy = monitor.total_energy_consumed()
            print(f"Total energy consumed: {total_energy:.2f} Wh")
            ```
        
        """

        total_energy_consumed: float = 0.0

        for component in self.__components:
            total_energy_consumed += self.__components[component].total_energy_consumed

        return total_energy_consumed

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
        """
        Starts the monitoring process in a separate thread.

        Example:
            Start the monitoring process:

            ```python
            from power_pyro import Monitor

            monitor = Monitor({'cpu': True, 'gpu': False, 'memory': True})
            monitor.start()
            ```
        """
        self.__thread.start()
    
    def is_running(self) -> bool:
        """
        Checks if the monitoring process is currently running.

        Returns:
            bool: True if the monitoring thread is alive (running), False otherwise.

        Example:
            Verify if the monitoring process is still running:

            ```python
            from power_pyro import Monitor

            monitor = Monitor({'cpu': True, 'gpu': False, 'memory': True})
            monitor.start()
            print(monitor.is_running())  # True, since monitoring has started
            monitor.end()
            print(monitor.is_running())  # False, since monitoring has ended
            ```
        """
        return self.__thread.is_alive()
    
    def end(self) -> None:
        """
        Stops the monitoring process and waits for the monitoring thread to finish.

        Example:
            Stop the monitoring process:

            ```python
            from power_pyro import Monitor

            monitor = Monitor({'cpu': True, 'gpu': False, 'memory': True})
            monitor.start()
            # ... perform operations to monitor ...
            monitor.end()  # Stops monitoring and waits for thread to finish
            ```
        """
        self.__stop_sign = True
        self.__thread.join()
