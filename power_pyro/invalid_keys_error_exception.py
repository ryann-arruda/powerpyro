class InvalidKeysErrorException(Exception):
    """Exception raised when the provided keys do not match the expected ones.

    Args:
        msg (str): Descriptive error message (optional). Default is "The keys provided do not match those expected".
    """
    def __init__(self, msg: str = "The keys provided do not match those expected"):
        super().__init__(msg)