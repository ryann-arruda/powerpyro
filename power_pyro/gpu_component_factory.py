from hardware_component_factory import HardwareComponentFactory
from os_type import OsType
from hardware_component import HardwareComponent
from gpu import Gpu
from identify_hardware_manufacturer_exception import IdentifyHardwareManufacturerException
from object_creation_exception import ObjectCreationException

class GpuComponentFactory(HardwareComponentFactory):
    """Factory class for creating GPU components.
    
    This class implements the 'HardwareComponentFactory' to provide concrete GPU components
    based on the specified operating system.
    """
    def __init__(self):
        super().__init__()
    
    def create_component(self, operating_system: OsType) -> HardwareComponent:
        try:
            return Gpu(operating_system)
        except IdentifyHardwareManufacturerException as e:
            raise ObjectCreationException(additional_info = str(e))