import sys
from Drone import *
from GlobalControlProcess import *
from multiprocessing import Process
import Pyro4
from Pyro4 import *
from Pyro4.naming import *
from Pyro4.core import *
from DroneSim1 import *
from DroneInputQueueContainer import *


class DroneSimController(GlobalControlProcess):
    
    # instance variable list
    #caoc - CAOC object, will be run in a new Process
    #imint - IMINT object, will be run in a new Process
    #drones - Drone objects, each will be run in a new Process
    #gvt - Global Virtual Time

    
    def __init__(self, caoc, imint):
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
        controllerInQ = Pyro4.Proxy(controllerInQ_uri)
        caocInQ_uri = nameserver.lookup('inputqueue.caoc')
        caocInQ = Pyro4.Proxy(caocInQ_uri)        
        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        imintInQ = Pyro4.Proxy(imintInQ_uri)
        droneInQs_uri = nameserver.lookup('inputqueue.drones')
        droneInQs = Pyro4.Proxy(droneInQs_uri)
            
        imintInQ.put('Controller Message to IMINT')        
        print 'In Controller:', imintInQ.get()
        caocInQ.put('Controller Message to CAOC')        
        print 'In Controller:', caocInQ.get() 
        controllerInQ.put('Controller Message to itself')        
        print 'In Controller:', controllerInQ.get()  
        
        print droneInQs.size()
        print list(droneInQs.keys())
        
        for drone in self.drones:
            dronename = drone.uid
            print dronename
            msg = 'Message to drone'
            droneInQs.addMessage(dronename, msg)    
        for drone in self.drones:
            dronename = drone.uid
            msg = droneInQs.getNextMessage(dronename)
            print msg      
        
        
        ## IMINT
        #pIMINT = Process(group=None, target=self.imint, name='IMINT Process')
        #pIMINT.start()
        
        ## Drones
        #pDrones = []
        #for i in range(0, len(self.drones)):
            #pDrone = Process(group=None, target=self.drones[i], name=self.drones[i].id) 
            #pDrones.append(pDrone)
            #pDrone.start()
        
        ## HMINT/CAOC
        #pCAOC = Process(group=None, target=self.caoc, name='HMINT/CAOC Process')
        #pCAOC.start()        
        
        ## Verify all processes running
        #while (not pIMINT.is_alive()):
            #time.sleep(100)
        #print('Detected IMINT alive')
        #while (not pCAOC.is_alive()):
            #time.sleep(100) 
        #print('Detected CAOC/HMINT alive')
        #for i in range(0, len(self.drones)):
            #dronename = 'Drone %d process' % (i)
            #pDrone = pDrones[i]
            #while (not pDrone.is_alive()):
                #time.sleep(100)
            #print('Detected drone alive')
            
        print "Time elapsed: ", time.time() - start_time, "s"
            
            