import sys
from Drone import *
from GlobalControlProcess import *
from multiprocessing import Process
import Pyro4
from DroneSim1 import *
from DroneInputQueueContainer import *


class DroneSimController(GlobalControlProcess):
    
    # instance variable list
    #caoc - CAOC object, will be run in a new Process
    #imint - IMINT object, will be run in a new Process
    #drones - Drone objects, each will be run in a new Process
    #gvt - Global Virtual Time

    
    def __init__(self, caoc, imint):
        GlobalControlProcess.__init__(self)
        self.caoc = caoc
        self.imint = imint
        self.drones = []
        self.gvt = 0
        
    def __call__(self):
        self.run()
        
    def addDrone(self, drone):
        self.drones.append(drone)
            
    def advanceTime(time):
        pass
    
    def updateGVT():
        minTimesList = []
        minTimesList.append(caoc.requestGVT())
        minTimesList.append(imint.requestGVT())
        for drone in drones:
            minTimesList.append(drone.requestGVT())
        gvt = min(minTimesList)
        
    def run(self):
        
        #Start the timer
        start_time = time.time()        
        
        # Self
        print('Drone Sim Controller running')
        
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
            
        self.imintInQ.put('Controller Message to IMINT')        
        self.caocInQ.put('Controller Message to CAOC')        
        self.controllerInQ.put('Controller Message to itself')        
        print 'In Controller:', self.controllerInQ.get()            
        
        msg = 'Message to drone' + str(2)
        self.droneInQs.addMessage(2, msg)
        
        msg = 'Message to drone' + str(1)
        self.droneInQs.addMessage(1, msg)
        
        msg = 'Message to drone' + str(0)
        self.droneInQs.addMessage(0, msg)         

            
        print "Time elapsed: ", time.time() - start_time, "s"
            
            