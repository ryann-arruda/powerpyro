from typing import Union

class ObjectCreationException(Exception):

    def __init__(self, msg:str = "Cannot create object", additional_info: Union[str, None] = None):
        if additional_info != None:
            super().__init__(msg + ": " + additional_info)
        else:
            super().__init__(msg)