import sys
import Pyro4
from LogicalProcess import *


class IMINT (LogicalProcess):
    
    # instance variable list
    #id - unique id for component
    #controller - the simulation executive   
        
    def __init__(self):
        self.id = 'IMINT'
        LogicalProcess.__init__(self)
    
    def __call__(self):
        self.run()
            
    def handleMessage(self, msg):
        # determine message type and process accordingly
        pass
    
    def run(self):
        
        print('IMINT Running')
    
        # Get the message queue objects from Pyro    
        nameserver = Pyro4.locateNS()
        controllerInQ_uri = nameserver.lookup('inputqueue.controller')
        self.controllerInQ = Pyro4.Proxy(controllerInQ_uri)
        caocInQ_uri = nameserver.lookup('inputqueue.caoc')
        self.caocInQ = Pyro4.Proxy(caocInQ_uri)        
        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        self.imintInQ = Pyro4.Proxy(imintInQ_uri)
        droneInQs_uri = nameserver.lookup('inputqueue.drones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
        
        print 'IMINT: ' + self.imintInQ.get()
        