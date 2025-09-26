from .hardware_component import HardwareComponent
from .os_type import OsType

import clr
import os
from abc import abstractmethod
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from LibreHardwareMonitor.Hardware import Computer

if os.name == 'nt':
    clr.AddReference(r"C:\LibreHardwareMonitor\LibreHardwareMonitorLib.dll")
    from LibreHardwareMonitor.Hardware import Computer

class ProcessingUnit(HardwareComponent):
    """Abstract base class representing a processing unit.
    
    This class extends 'HardwareComponent' and provides common functionality
    for processing units, including name management and computer interaction.
    """
    def __init__(self, operating_system: OsType):
        super().__init__(operating_system)

        self.__name: str = None

        if operating_system == OsType.WINDOWS:
            self.__computer: "Computer" = Computer()

    @property
    def name(self) -> str:
        """Gets the name of the processing unit.

        Returns:
            str: The name of the processing unit.
        """
        return self.__name
    
    @name.setter
    def set_name(self, name: str) -> None:
        """Sets the name of the processing unit.
        
        Args:
            name (str): The new name of the processing unit.
        """
        self.__name = name
    
    @property
    def computer(self) -> Union["Computer", None]:
        """Gets the computer instance associated with the processing unit.

        Returns:
            Union[Computer, None]: Gets the computer instance associated with 
                                   the processing unit, or None if not on Windows OS.
        """
        if self.operating_system == OsType.WINDOWS:
            return self.__computer
        
        return None
    
    def open(self) -> None:
        """Opens the computer monitoring instance."""
        if self.operating_system == OsType.WINDOWS:
            self.__computer.Open()
    
    def close(self) -> None:
        """Closes the computer monitoring instance."""
        if self.operating_system == OsType.WINDOWS:
            self.__computer.Close()
    
    @abstractmethod
    def _update_manufacture(self) -> None:
        pass

    @abstractmethod
    def _update_hardware_name(self) -> None:
        pass
