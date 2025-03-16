class ResourceUnavailableException(Exception):

    def __init__(self, resource_name:str, msg:str):
        super().__init__(resource_name + " : " + msg)