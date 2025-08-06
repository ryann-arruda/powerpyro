from .processing_unit import ProcessingUnit
from .gpu_type import GpuType
from .os_type import OsType
from .identify_hardware_manufacturer_exception import IdentifyHardwareManufacturerException
from .hardware_name_identify_exception import HardwareNameIdentifyException
from .resource_unavailable_exception import ResourceUnavailableException
from .hardware_type import HardwareType as HT

import time
import subprocess
import re
import os
import clr

if os.name == 'nt':

    #clr.AddReference(r"C:\Users\Alexa\OneDrive\Área de Trabalho\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    clr.AddReference(r"C:\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType

class Gpu(ProcessingUnit):
    """Represents a Graphics Processing Unit (GPU) responsible 
       for accessing and retrieving power consumption values 
       ​​from hardware sensors.

    Attributes:
        __manufacturer (GpuType): GPU  type.
    """

    def __init__(self, operating_system: OsType):
        super().__init__(operating_system)
        self.__manufacturer: GpuType

        if operating_system == OsType.WINDOWS:
            self.computer.IsGpuEnabled = True        

        self._update_manufacture()
        self._update_hardware_name()
    
    @property
    def get_manufacturer(self) -> GpuType:
        """ The hardware manufacturer.

        Returns:
            GpuType: A type of GPU.

        Example:
            ```python

            from monitor import Monitor

            monitor = Monitor({'gpu': True})

            components = monitor.get_monitored_components()
            print(components['gpu']['component'].get_manufacturer) #GpuType.NVIDIA

            ```
        """
        return self.__manufacturer
    
    def __is_there_dedicated_gpu_windows(self) -> bool:
        """ Check if it is a dedicated gpu in Windows OS.

        Returns:
            bool: 
                - 'True' if a dedicated gpu is found on Windows.
                - 'False' if a dedicated gpu is not found in Windows.
        """
        computer = Computer()
        computer.Open()
        computer.IsGpuEnabled = True

        gpu = next((hardware for hardware in computer.Hardware if (hardware.HardwareType == HardwareType.GpuIntel or
                                                                   hardware.HardwareType == HardwareType.GpuAmd or
                                                                   hardware.HardwareType == HardwareType.GpuNvidia)), None)
        
        if gpu != None:
            gpu.Update()
            time.sleep(0.1)

            if next((sensor for sensor in gpu.Sensors if sensor.Name == "D3D Dedicated Memory Used"), None) != None:
                computer.Close()
                return True
        
        computer.Close()
        return False
    
    def _update_manufacture(self) -> None:
        if self.operating_system == OsType.WINDOWS:
            self.__update_manufacture_windows()
        
        elif self.operating_system == OsType.LINUX:
            self.__update_manufacture_linux()
        else:
            raise OSError("Unable to identify operating system")

    def __update_manufacture_windows(self) -> None:
        """Update hardware manufacturer when running on Windows OS.
        
        Raises:
            IdentifyHardwareManufacturerException: If the hardware manufacturer 
            cannot be identified.

            ResourceUnavailableException: If a dedicated GPU is not found in Windows.
        """
        if not self.__is_there_dedicated_gpu_windows():
            raise ResourceUnavailableException("GPU", "Resource not found!")
        
        computer = Computer()
        computer.Open()
        computer.IsGpuEnabled = True

        for hardware in computer.Hardware:
            hardware_type = str(hardware.HardwareType)

            if hardware_type == 'GpuNvidia':
                self.__manufacturer = GpuType.NVIDIA
            elif hardware_type == 'GpuAmd':
                self.__manufacturer = GpuType.AMD
            else:
                raise IdentifyHardwareManufacturerException(HT.GPU)
        
        computer.Close()

    def __update_manufacture_linux(self) -> None:
        """Update hardware manufacturer when running on Linux OS.
        
        Raises:
            IdentifyHardwareManufacturerException: If the hardware manufacturer
            cannot be identified.
        """

        if self.__is_there_nvidia_on_linux():
            self.__manufacturer = GpuType.NVIDIA
        elif self.__is_there_amd_on_linux():
            self.__manufacturer = GpuType.AMD
        else:
            raise IdentifyHardwareManufacturerException(HT.GPU)
    
    def _update_hardware_name(self) -> None:
        if self.operating_system == OsType.WINDOWS:
            self.__update_hardware_name_windows()
        elif self.operating_system == OsType.LINUX:
            self.__update_hardware_name_linux
        else:
            raise OSError("Unable to identify operating system")
    
    def __update_hardware_name_windows(self) -> None:
        """ Set the GPU name.
        
        Raises:
            ResourceUnavailableException: If a dedicated GPU is not found in Windows.
        """
        if not self.__is_there_dedicated_gpu_windows():
            raise ResourceUnavailableException("GPU", "Resource not found!")
        
        computer = Computer()
        computer.Open()
        computer.IsGpuEnabled = True

        for hardware in computer.Hardware:
            self.set_name = hardware.Name
        
        computer.Close()
    
    def __update_hardware_name_linux(self) -> None:
        """ Set the GPU name.
        
        Raises:
            HardwareNameIdentifyException: Unable to identify GPU name in Linux.
        """
        try:
            if self.__is_there_nvidia_on_linux():
                self.set_name = subprocess.check_output("nvidia-smi --query-gpu=name --format=csv,noheader", shell=True).decode().strip()
            elif self.__is_there_amd_on_linux():
                output = subprocess.check_output("lspci | grep -i vga", shell=True).decode().strip()
                self.set_name = re.findall(r'\w+ \w+ \w+ \w+ / \w+ \w+\W\w+', output)
            else:
                raise HardwareNameIdentifyException(HT.GPU)
        except (FileNotFoundError, subprocess.CalledProcessError, UnicodeDecodeError):
            raise HardwareNameIdentifyException(HT.GPU)
    
    def get_power(self) -> float:
        if self.operating_system == OsType.WINDOWS:
            return self.__get_power_on_windows()

        else:
            if self.__manufacturer == GpuType.NVIDIA:
                return self.__get_nvidia_power_on_linux()
            elif self.__manufacturer == GpuType.AMD:
                return self.__get_amd_power_on_linux()

    def __get_power_on_windows(self) -> float:
        """ Returns the value of the GPU power in W in Windows.

        Returns:
            float: GPU power.
        """
        gpu = next((hardware for hardware in self.computer.Hardware if (hardware.HardwareType == HardwareType.GpuIntel or
                                                                        hardware.HardwareType == HardwareType.GpuAmd or
                                                                        hardware.HardwareType == HardwareType.GpuNvidia)), None)
        gpu.Update()
        time.sleep(0.1)

        power = next((sensor for sensor in gpu.Sensors if sensor.SensorType == SensorType.Power and (sensor.Name == "GPU Power" or sensor.Name == "GPU Package")))
        return power.Value

    def __is_there_nvidia_on_linux(self) -> bool:
        """ Check if the GPU present in linux is NVIDIA.

        Returns:
            bool: 
                - 'True' if you have NVIDIA GPU on linux.
                - 'False' if you don't have NVIDIA GPU on linux.
        """
        try:
            subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr= subprocess.PIPE, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
    
    def __get_nvidia_power_on_linux(self) -> float:
        """ Returns the value of the NVIDIA GPU power in W in Linux.

        Returns:
            float: GPU power.
        """
        try:
            result = subprocess.run(["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    check=True)
            
            return float(result.stdout.strip())
        except Exception as e:
            print('Error getting power from GPU: ', str(e))
            return 0.0
    
    def __is_there_amd_on_linux(self) -> bool:
        """ Check if the GPU present in Linux is AMD.

        Returns:
            bool: 
                - 'True' if you have AMD GPU on Linux.
                - 'False' if you don't have AMD GPU on Linux.

        Raises:
            Exception: Error when checking AMD dedicated video card on Linux.
        """
        try:
            result = subprocess.check_output(['lspci', '-nnk'], universal_newlines=True)

            for line in result.splitlines():
                if re.search(r"( VGA | 3D )", line) and re.search(r"AMD", line.upper()): 
                    return True
            
            return False
        except Exception as e:
            raise Exception(f'Error checking for AMD graphics card:{e}')   
    
    def __get_amd_power_on_linux(self) -> float:
        """ Returns the value of the AMD GPU power in W in Linux.

        Returns:
            float: GPU power.
        """
        try:
            hwmon_path = '/sys/class/hwmon/'

            for hwmon in os.listdir(hwmon_path):
                hwmon_dir = os.path.join(hwmon_path, hwmon)
                
                name_file = os.path.join(hwmon_dir, 'name')
                if os.path.exists(name_file):
                    with open(name_file, 'r') as file:
                        device = file.read().strip()

                    if device == 'amdgpu':
                        power_file = os.path.join(hwmon_dir, 'power1_input')
                        if os.path.exists(power_file):
                            with open(power_file, 'r') as file:
                                power = float(file.read().strip())

                            power /= 10**6
                            return power
        except (FileNotFoundError, PermissionError, ValueError) as e:
            print('Error getting power from GPU: ', str(e))
