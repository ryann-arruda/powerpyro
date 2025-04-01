class ResourceUnavailableException(Exception):
    """Exception raised when a requested resource is unavailable.

    Args:
        resource_name (str): Name of the resource that is unavailable.
        msg (str): Descriptive error message providing more details about the unavailability.
    """
    def __init__(self, resource_name: str, msg: str):
        super().__init__(resource_name + " : " + msg)
