from SharedMemoryClient import *

class GlobalControlProcess(SharedMemoryClient):
    
    def __init__(self):
        SharedMemoryClient.__init__(self)