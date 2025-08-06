from .hardware_component_factory import HardwareComponentFactory
from .os_type import OsType
from .hardware_component import HardwareComponent
from .memory import Memory
from .object_creation_exception import ObjectCreationException

class MemoryComponentFactory(HardwareComponentFactory):
    """Factory class for creating Memory components.
    
    This class implements the 'HardwareComponentFactory' to provide concrete Memory components
    based on the specified operating system.
    """
    def __init__(self):
        super().__init__()

    def create_component(self, operating_system: OsType) -> HardwareComponent:
        """Creates a memory hardware component based on the provided operating system.

            Args:
                operating_system (OsType): The type of operating system for 
                which the memory component will be created.

            Returns:
                HardwareComponent: An instance of the memory component 
                corresponding to the given operating system.

            Raises:
                ObjectCreationException: If an OS-level error occurs during 
                memory component creation.
    """
        try:
            return Memory(operating_system)
        except OSError as e:
            raise ObjectCreationException(additional_info = str(e))