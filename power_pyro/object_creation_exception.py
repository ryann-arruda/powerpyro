from typing import Union

class ObjectCreationException(Exception):
    """Exception raised when an object cannot be created.

    Args:
        msg (str): Descriptive error message 
        (optional, default is "Cannot create object").
        additional_info (Union[str, None]): Additional information about the 
        error (optional).
    """
    def __init__(self, msg: str = "Cannot create object", additional_info: Union[str, None] = None):
        if additional_info is not None:
            super().__init__(msg + ": " + additional_info)
        else:
            super().__init__(msg)
