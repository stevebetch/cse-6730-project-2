from SharedMemoryClient import *

# Super class for simulation controller
class GlobalControlProcess(SharedMemoryClient):
    
    CONTROLLER_ID = 'Controller'
    
    def __init__(self):
        SharedMemoryClient.__init__(self)