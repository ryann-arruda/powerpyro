from processing_unit import ProcessingUnit
from gpu_type import GpuType
from os_type import OsType
from identify_hardware_manufacturer_exception import IdentifyHardwareManufacturerException
from resource_unavailable_exception import ResourceUnavailableException
from hardware_type import HardwareType as HT

from time import time
import subprocess
import re
import os
from elevate import elevate
import clr

if os.name == 'nt':
    elevate()

    #clr.AddReference(r"C:\Users\Alexa\OneDrive\Área de Trabalho\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    clr.AddReference(r"C:\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    from LibreHardwareMonitor.Hardware import Computer, HardwareType, SensorType

class Gpu(ProcessingUnit):
    def __init__(self, operating_system: OsType):
        super().__init__(operating_system)
        self.__manufacturer: GpuType

        if operating_system == OsType.WINDOWS:
            self.get_computer().IsGpuEnabled = True        

        self.__update_manufacture()
    
    def __is_there_dedicated_gpu_windows(self) -> bool:
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
    
    def __update_manufacture(self) -> None:
        
        if self.get_operating_system() == OsType.WINDOWS:
            self.__update_manufacture_windows()
        
        elif self.get_operating_system() == OsType.LINUX:
            self.__update_manufacture_linux()
        else:
            raise OSError("Unable to identify operating system")

    def __update_manufacture_windows(self) -> None:

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
        if self.__is_there_nvidia_on_linux():
            self.__manufacturer = GpuType.NVIDIA
        elif self.__is_there_amd_on_linux():
            self.__manufacturer = GpuType.AMD
        else:
            raise IdentifyHardwareManufacturerException(HT.GPU)
    
    def get_power(self) -> float:

        if self.get_operating_system() == OsType.WINDOWS:
            return self.__get_power_on_windows()

        else:
            if self.__manufacturer == GpuType.NVIDIA:
                return self.__get_nvidia_power_on_linux()
            elif self.__manufacturer == GpuType.AMD:
                return self.__get_amd_power_on_linux()

    def __get_power_on_windows(self) -> float:
        gpu = next((hardware for hardware in self.get_computer().Hardware if (hardware.HardwareType == HardwareType.GpuIntel or
                                                                        hardware.HardwareType == HardwareType.GpuAmd or
                                                                        hardware.HardwareType == HardwareType.GpuNvidia)), None)
        gpu.Update()
        time.sleep(0.1)

        power = next((sensor for sensor in gpu.Sensors if sensor.SensorType == SensorType.Power and (sensor.Name == "GPU Power" or sensor.Name == "GPU Package")))
        return power.Value

    def __is_there_nvidia_on_linux(self) -> bool:
        try:
            subprocess.run(['nvidia-smi'], stdout=subprocess.PIPE, stderr= subprocess.PIPE, check=True)
            return True
        except FileNotFoundError:
            return False
        except subprocess.CalledProcessError:
            return False
    
    def __get_nvidia_power_on_linux(self) -> float:
        if self._nvidia_gpu: 
            try:
                result = subprocess.run(["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True,
                                        check=True)
                
                return float(result.stdout.strip())
            except Exception as e:
                print('Error getting power from GPU: ', e.stderr.strip())
                return 0.0
    
    def __is_there_amd_on_linux(self) -> bool:
        try:
            result = subprocess.check_output(['lspci', '-nnk'], universal_newlines=True)

            for line in result.splitlines():
                if re.search(r"( VGA | 3D )", line) and re.search(r"AMD", line.upper()): 
                    return True
            
            return False
        except Exception as e:
            raise Exception(f'Error checking for AMD graphics card:{e}')    
    
    def __get_amd_power_on_linux(self) -> float:
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
        except FileNotFoundError as e:
            print('Error getting power from GPU: ', e.stderr.strip())