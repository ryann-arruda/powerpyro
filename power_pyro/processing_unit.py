from hardware_component import HardwareComponent
from os_type import OsType

import clr
import os
from abc import abstractmethod

if os.name == 'nt':

    #clr.AddReference(r"C:\Users\Alexa\OneDrive\Área de Trabalho\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    clr.AddReference(r"C:\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    from LibreHardwareMonitor.Hardware import Computer

class ProcessingUnit(HardwareComponent):

    def __init__(self, operating_system: OsType):
        super().__init__(operating_system)

        if operating_system == OsType.WINDOWS:
            self.__computer: Computer = Computer()
    
    def get_computer(self) -> Computer:
        return self.__computer
    
    def open(self) -> None:
        self.__computer.Open()
    
    def close(self) -> None:
        self.__computer.Close()
    
    @abstractmethod
    def _update_manufacture(self) -> None:
        pass