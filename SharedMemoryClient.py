import Pyro4

class SharedMemoryClient:
    
    def __init__(self):
        pass
    
    def setConnectionParams(self, p_host, p_port):
        self.PYRO_HOST = p_host
        self.PYRO_PORT = p_port
        
    
  