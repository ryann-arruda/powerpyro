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

        self.__name:str = None

        if operating_system == OsType.WINDOWS:
            self.__computer: Computer = Computer()

    def get_name(self) -> str:
        return self.__name
    
    def set_name(self, name:str) -> None:
        self.__name = name
    
    def get_computer(self) -> Computer:
        return self.__computer
    
    def open(self) -> None:
        self.__computer.Open()
    
    def close(self) -> None:
        self.__computer.Close()
    
    @abstractmethod
    def _update_manufacture(self) -> None:
        pass

    @abstractmethod
    def _update_hardware_name(self) -> None:
        pass