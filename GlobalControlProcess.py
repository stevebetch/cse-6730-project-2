from SharedMemoryClient import *

class GlobalControlProcess(SharedMemoryClient):
    
    CONTROLLER_ID = 'Controller'
    
    def __init__(self):
        SharedMemoryClient.__init__(self)