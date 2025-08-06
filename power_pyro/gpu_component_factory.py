from .hardware_component_factory import HardwareComponentFactory
from .os_type import OsType
from .hardware_component import HardwareComponent
from .gpu import Gpu
from .identify_hardware_manufacturer_exception import IdentifyHardwareManufacturerException
from .object_creation_exception import ObjectCreationException

class GpuComponentFactory(HardwareComponentFactory):
    """Factory class for creating GPU components.
    
    This class implements the 'HardwareComponentFactory' to provide concrete GPU components
    based on the specified operating system.
    """
    def __init__(self):
        super().__init__()
    
    def create_component(self, operating_system: OsType) -> HardwareComponent:
        """Creates a GPU hardware component based on the provided operating system.

            Args:
                operating_system (OsType): The type of operating system for 
                which the GPU component will be created.

            Returns:
                HardwareComponent: An instance of the GPU component 
                corresponding to the given operating system.

            Raises:
                ObjectCreationException: If an error occurs while 
                identifying the hardware manufacturer.
        """
        try:
            return Gpu(operating_system)
        except IdentifyHardwareManufacturerException as e:
            raise ObjectCreationException(additional_info = str(e))