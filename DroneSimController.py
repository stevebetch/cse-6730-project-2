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
        #self.imintInQ.addMessage(Message(1, 'Data', 'Controller', 'IMINT', 5))
        #self.caocInQ.addMessage(Message(1, 'Data', 'Controller', 'CAOC', 2))
        #self.caocInQ.addMessage(Message(1, 'Data', 'Controller', 'CAOC', 3))
        #self.caocInQ.addMessage(Message(1, 'Data', 'Controller', 'CAOC', 4))
        #self.caocInQ.addMessage(Message(1, 'Data', 'Controller', 'CAOC', 5))
        #self.inputQueue.addMessage(Message(1, 'Data', 'Controller', 'Controller', 3))
         
        while True:
            
            time.sleep(10)
            
            # GVT: Trigger round for cut C1 (CAOC is first LP in token ring)
            print 'Controller sending cut C1 token to first LP'
            self.caocInQ.addMessage(Message(1, GVTControlMessageData(self.gvtTokenRing), 'Controller', 'CAOC', -1))
            msg = None
            print 'Controller waiting for cut C1 token'
            sys.stdout.flush()            
            while True:
                time.sleep(0)
                msg = self.inputQueue.getNextMessage()
                if not(msg is None):
                    if isinstance(msg.data, GVTControlMessageData):
                        break
            
            print 'Controller received GVT control token back from LPs (Cut C1)'
            sys.stdout.flush()
        
            count = 0
            for i in msg.data.counts:
                print 'GVT counts[%d] = %d (after cut C1)' % (i, msg.data.counts[i])
                count += msg.data.counts[i]
            print 'Total counts in GVT = %d (after cut C1)' % (count)
            if count <= 0:
                # GVT: Send GVT value to all LPs
                print 'Controller sending GVT value to first LP'
                sys.stdout.flush()
                gvt = min(msg.data.tMin, msg.data.tRed)
                self.caocInQ.addMessage(Message(1, GVTValue(gvt), 'Controller', 'IMINT', -1))                  
            else:
                # GVT: Trigger round for cut C2
                print 'Controller sending cut C2 token to first LP'
                sys.stdout.flush()
                self.caocInQ.addMessage(msg)
                print 'Controller waiting for cut C2 token'
                sys.stdout.flush()                
                while True:
                    time.sleep(0)                    
                    msg = self.inputQueue.getNextMessage()
                    if not(msg is None):
                        if isinstance(msg.data, GVTControlMessageData):
                            break
                
                print 'Controller received GVT control token back from LPs (Cut C2)'
                count = 0
                for i in msg.data.counts:
                    print 'GVT counts[%d] = %d (after cut C2)' % (i, msg.data.counts[i])
                    count += msg.data.counts[i]
                print 'Total counts in GVT = %d (after cut C2)' % (count)  
                # GVT: Send GVT value to all LPs
                print 'Controller sending GVT value to first LP'
                sys.stdout.flush()
                gvt = min(msg.data.tMin, msg.data.tRed)
                print 'GVT value is %d' % (gvt)
                self.caocInQ.addMessage(Message(1, GVTValue(gvt), 'Controller', 'IMINT', -1))                 
                sys.stdout.flush()                
            break

        print "Time elapsed: ", time.time() - start_time, "s"

