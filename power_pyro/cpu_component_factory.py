from .hardware_component_factory import HardwareComponentFactory
from .os_type import OsType
from .hardware_component import HardwareComponent
from .cpu import Cpu
from .identify_hardware_manufacturer_exception import IdentifyHardwareManufacturerException
from .object_creation_exception import ObjectCreationException

class CpuComponentFactory(HardwareComponentFactory):
    """Factory class for creating CPU components.
    
    This class implements the 'HardwareComponentFactory' to provide concrete CPU components
    based on the specified operating system.
    """
    def __init__(self):
        super().__init__()

    def create_component(self, operating_system: OsType) -> HardwareComponent:
        """Creates a hardware component based on the provided operating system.

            Args:
                operating_system (OsType): The type of operating system for 
                which the component will be created.

            Returns:
                HardwareComponent: An instance of the hardware component 
                corresponding to the given operating system.

            Raises:
                ObjectCreationException: If an error occurs while identifying 
                the hardware manufacturer. 
        """
        try:
            return Cpu(operating_system)
        except IdentifyHardwareManufacturerException as e:
            raise ObjectCreationException(additional_info = str(e))