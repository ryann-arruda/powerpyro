from processing_unit import ProcessingUnit
from cpu_type import CpuType
from os_type import OsType
from identify_hardware_manufacturer_exception import IdentifyHardwareManufacturerException
from hardware_name_identify_exception import HardwareNameIdentifyException
from hardware_type import HardwareType as HT

import os
import clr
import wmi
import cpuinfo
import subprocess
import time
import psutil

if os.name == 'nt':

    #clr.AddReference(r"C:\Users\Alexa\OneDrive\Área de Trabalho\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    clr.AddReference(r"C:\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    from LibreHardwareMonitor.Hardware import HardwareType, SensorType

class Cpu(ProcessingUnit):
    """Represents a Central Processing Unit (CPU) responsible 
       for accessing and retrieving power consumption values 
       ​​from hardware sensors.

    Attributes:
        __manufacturer (CpuType): CPU  type.
    """
    def __init__(self, operating_system: OsType):
        super().__init__(operating_system)
        self.__manufacturer: CpuType

        if operating_system == OsType.WINDOWS:
            self.computer().IsCpuEnabled = True
        
        self._update_manufacture()
    
    @property
    def get_manufacturer(self) -> CpuType:
        """ The hardware manufacturer.

        Returns:
            GpuType: A type of CPU.
        """
        return self.__manufacturer

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
        """

        try:
            wmi_session = wmi.WMI()

            manufacturer = wmi_session.Win32_Processor()[0].Manufacturer

            if manufacturer == 'GenuineIntel':
                self.__manufacturer = CpuType.INTEL
            elif manufacturer == 'AuthenticAMD':
                self.__manufacturer = CpuType.AMD
            else:
                raise IdentifyHardwareManufacturerException(HT.CPU)
        except (ModuleNotFoundError, wmi.x_wmi, IndexError, AttributeError):
            raise IdentifyHardwareManufacturerException(HT.CPU)

    def __update_manufacture_linux(self) -> None:
        """Update hardware manufacturer when running on Linux OS.
        
        Raises:
            IdentifyHardwareManufacturerException: If the hardware manufacturer 
            cannot be identified.
        """
        
        try:
            info = cpuinfo.get_cpu_info()

            manufacturer = info['vendor_id_raw']

            if manufacturer == 'GenuineIntel':
                self.__manufacturer = CpuType.INTEL
            elif manufacturer == 'AuthenticAMD':
                self.__manufacturer = CpuType.AMD
            else:
                raise IdentifyHardwareManufacturerException(HT.CPU)
        except (ModuleNotFoundError, KeyError):
            raise IdentifyHardwareManufacturerException(HT.CPU)
    
    def _update_hardware_name(self) -> None:
        if self.operating_system == OsType.WINDOWS:
            self.__update_hardware_name_windows()
        elif self.operating_system == OsType.LINUX:
            self.__update_hardware_name_linux()
        else:
            raise OSError("Unable to identify operating system")
    
    def __update_hardware_name_windows(self) -> None:
        """ Set the CPU name.
        
        Raises:
            HardwareNameIdentifyException: Unable to identify CPU name in Windows.
        """
        
        try:
            wmi_session = wmi.WMI()

            self.set_name(wmi_session.Win32_Processor()[0].Name)
        except (ModuleNotFoundError, wmi.x_wmi, IndexError, AttributeError):
            raise HardwareNameIdentifyException(HT.CPU)

    def __update_hardware_name_linux(self) -> None:
        """ Set the CPU name.
        
        Raises:
            HardwareNameIdentifyException: Unable to identify CPU name in Linux.
        """

        try:
            self.set_name(cpuinfo.get_cpu_info()['brand_raw'])
        except (ModuleNotFoundError, KeyError):
            raise HardwareNameIdentifyException(HT.CPU)
    
    def get_power(self) -> float:
        if self.operating_system == OsType.WINDOWS:
            return self.__get_power_on_windows()

        else:
            return self.__get_power_on_linux()
    
    def __get_power_on_linux(self) -> float:
        """" Returns the value of the CPU power in W in Linux.

        Returns:
            float: CPU power.
        """

        try:
            command = ["sudo", "perf", "stat", "-e", "power/energy-pkg/", "sleep", "0.1"]
            power = subprocess.run(command, capture_output=True, text=True)

            power = power.stderr.split(" ")
            power = [string for string in power if string.strip()]

            for index, string in enumerate(power):
                if string.find('\n\n') != -1:
                    power = power[index + 1]
                    power = power.replace(",", ".")
                    break
            
            power = float(power)/0.1
        except (PermissionError, subprocess.SubprocessError, AttributeError, IndexError, ValueError) as e:
            print('Error getting power from CPU: ', str(e))

        return power

    def __get_power_on_windows(self) -> float:
        """" Returns the value of the CPU power in W in Windows.

        Returns:
            float: CPU power.
        """
        try:
            cpu = next((hardware for hardware in self.computer().Hardware if hardware.HardwareType == HardwareType.Cpu), None)
            cpu.Update()
            time.sleep(0.1)

            power = next((sensor for sensor in cpu.Sensors if sensor.SensorType == SensorType.Power and (sensor.Name == "CPU Package" or sensor.Name == "Package")))
            power = power.Value
        except AttributeError as e:
            print('Error getting power from CPU: ', str(e))

        return power

    def get_cpu_percent_for_process(self) -> float:
        """" Returns the percentage value of the monitored process on the CPU.

        Returns:
            float: CPU percent.
        """
        script_pid = os.getpid()
        sum_all = 0
        cpu_percent = 0
        for process in psutil.process_iter():
            try:
                with process.oneshot():
                    process_pid = process.pid
                    process_cpu_percent = process.cpu_percent()

                    if process_pid:
                        sum_all += process_cpu_percent

                        if process_pid == script_pid:
                            cpu_percent += process_cpu_percent
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
            
        if sum_all != 0:
            return cpu_percent/sum_all
        else:
            return 0.0