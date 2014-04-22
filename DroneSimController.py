import sys,time
from Drone import *
from GlobalControlProcess import *
from GVT import *
from multiprocessing import Process
import Pyro4
from DroneSim1 import *
from DroneInputQueueContainer import *
import Queue


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
        self.gvtTokenRing = [self.imint.LPID, self.caoc.LPID]

    def __call__(self):
        self.run()

    def addDrone(self, drone):
        self.drones.append(drone)
        self.gvtTokenRing.append(drone.LPID)

    def run(self):

        #Start the timer
        start_time = time.time()        

        # Self
        print('Drone Sim Controller running')

        # Get the message queue objects from Pyro    
        nameserver = Pyro4.locateNS()
        
        controllerInQ_uri = nameserver.lookup('inputqueue.controller')
        self.inputQueue = Pyro4.Proxy(controllerInQ_uri)
        
        caocInQ_uri = nameserver.lookup('inputqueue.caoc')
        self.caocInQ = Pyro4.Proxy(caocInQ_uri)
        
        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        self.imintInQ = Pyro4.Proxy(imintInQ_uri)
        
        droneInQs_uri = nameserver.lookup('inputqueue.drones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
        
        # Mark: Test code can be commented out
        self.imintInQ.addMessage(Message(1, 'Data', 'Controller', 'IMINT', 5))
        self.caocInQ.addMessage(Message(1, 'Data', 'Controller', 'CAOC', 2))
        self.caocInQ.addMessage(Message(1, 'Data', 'Controller', 'CAOC', 3))
        self.caocInQ.addMessage(Message(1, 'Data', 'Controller', 'CAOC', 4))
        self.caocInQ.addMessage(Message(1, 'Data', 'Controller', 'CAOC', 5))
        self.inputQueue.addMessage(Message(1, 'Data', 'Controller', 'Controller', 3))
#        print 'In Controller:', self.inputQueue.getNextMessage()                    
#        msg = 'Message to drone' + str(2)
#        self.droneInQs.addMessage(2, Message(1, 'Data', 'Controller', 'Drone', 6))     
#        msg = 'Message to drone' + str(1)
#        self.droneInQs.addMessage(1, Message(1, 'Data', 'Controller', 'Drone', 7))      
#        msg = 'Message to drone' + str(0)
#        self.droneInQs.addMessage(0, Message(1, 'Data', 'Controller', 'Drone', 5))         
        time.sleep(10)
        while False:
            # GVT: Trigger round for cut C1 (CAOC is first LP in token ring)
            print 'Controller sending cut C1 token to first LP'
            sys.stdout.flush()
            self.caocInQ.addMessage(Message(1, GVTControlMessageData(self.gvtTokenRing), 'Controller', 'CAOC', self.gvt + 100)) # timestamp value??
            msg = None
            while True:
                time.sleep(0.1)
                print 'Controller waiting for cut C1 token'
                sys.stdout.flush()
                msg = self.inputQueue.getNextMessage()
                if not(msg is None):
                    if isinstance(msg.data, GVTControlMessageData):
                        break
            
            print 'Controller received GVT control token back from LPs (Cut C1)'
            msg.dump()
            sys.stdout.flush()
            #count = 0
            #for i in msg.data.counts:
                #count += msg.data.counts[i]
            #if count > 0:
                ## GVT: Send GVT value to all LPs
                #print 'Controller sending GVT value to first LP'
                #sys.stdout.flush()
                #gvt = min(msg.data.tMin, msg.data.tRed)
                #self.caocInQ.addMessage(Message(1, GVTValue(gvt), 'Controller', 'IMINT', self.gvt + 110)) # timestamp value??                  
            #else:
                ## GVT: Trigger round for cut C2
                #print 'Controller sending cut C2 token to first LP'
                #sys.stdout.flush()
                #self.caocInQ.addMessage(msg)

        print "Time elapsed: ", time.time() - start_time, "s"

