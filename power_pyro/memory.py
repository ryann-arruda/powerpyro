from hardware_component import HardwareComponent
from os_type import OsType

import os
import psutil
import wmi
import subprocess
import re

class Memory(HardwareComponent):
    """Represents a Memory component responsible for calculating power consumption
       based on the amount of memory used.

    Attributes:
        __WATT_PER_GB (float): Power consumption per GB of memory.
    """
    def __init__(self, operating_system: OsType):
        super().__init__(operating_system)
        self.__WATT_PER_GB: float = self.__watt_per_gb()
    
    def __watt_per_gb(self) -> float:
        """Calculates the power consumption per GB of memory.

        Returns:
            float: Power consumption per GB of memory.
        
        Raises:
            OSError: If the operating system is not recognized.
        """
        if self.get_operating_system() == OsType.WINDOWS:
            return self.__watt_per_gb_on_windows()
        elif self.get_operating_system() == OsType.LINUX:
            return self.__watt_per_gb_on_linux()
        else:
            raise OSError("Unable to identify operating system")

    def __watt_per_gb_on_windows(self) -> float:
        """Calculates the power consumption per GB of memory on Windows OS.

        Returns:
            float: Power consumption per GB.

        Raises:
            RuntimeError: Unable to get information from memory.
        """
        try:
            BYTES_TO_GIGABYTES = 1024**3
            wmi_session = wmi.WMI()

            num_memory_modules = len(wmi_session.Win32_PhysicalMemory())

            memory_module = wmi_session.Win32_PhysicalMemory()[0]
            gb_per_module = int(memory_module.Capacity)/BYTES_TO_GIGABYTES
        except (ModuleNotFoundError, IndexError, TypeError, wmi.x_wmi):
            raise RuntimeError("Unable to get watts per GB information from memory")

        return (5 * num_memory_modules)/gb_per_module        
    
    def __watt_per_gb_on_linux(self) -> float:
        """Calculates the power consumption per GB of memory on Linux OS.

        Returns:
            float: Power consumption per GB.

        Raises:
            RuntimeError: Unable to get information from memory.
        """
        try:
            output = subprocess.check_output(["sudo", "dmidecode", "-t", "memory"], universal_newlines=True)

            num_memory_modules_found = len(re.findall(r"\tSize:", output))
            number_unused_memory_modules = len(re.findall(r"Size: No Module Installed", output))

            num_memory_modules = num_memory_modules_found - number_unused_memory_modules
            
            gb_per_module = re.findall(r"\tSize: \d+ \w+", output)
            gb_per_module = gb_per_module[0].split(": ")
            gb_per_module = gb_per_module[1].split(" ")
            gb_per_module = int(gb_per_module[0])
        except (FileNotFoundError, PermissionError, subprocess.CalledProcessError, IndexError, ValueError):
            raise RuntimeError("Unable to get watts per GB information from memory")

        return (5 * num_memory_modules)/gb_per_module 
    
    def get_power(self) -> float:
        """Returns the power consumption of the memory in W.

        Returns:
            float: Memory power consumption.
        """
        try:
            pid = os.getpid()
            process = psutil.Process(pid)

            power = process.memory_info().rss
            power /= (1024 ** 3)
            power *= self.__WATT_PER_GB
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print('Error getting power from memory:', str(e))
        
        return power