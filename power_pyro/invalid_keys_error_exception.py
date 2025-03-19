from typing import Dict

class InvalidKeysErrorException(Exception):
    
    def __init__(self, msg: str = "The keys provided do not match those expected"):
        super().__init__(msg)