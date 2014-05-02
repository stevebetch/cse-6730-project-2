import Pyro4

# base class for types needing to connect to Pyro4 name server
class SharedMemoryClient:
    
    def __init__(self):
        pass
    
    # Sets the Pyro4 name server connection parameters
    def setConnectionParams(self, p_host, p_port):
        self.PYRO_HOST = p_host
        self.PYRO_PORT = p_port
        
    
  