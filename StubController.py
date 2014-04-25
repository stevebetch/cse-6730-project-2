import sys,time
from Drone import *
from GlobalControlProcess import *
from GVT import *
from HMINT import *
from multiprocessing import Process
import Pyro4
from DroneSim1 import *
from DroneInputQueueContainer import *
import Queue


class StubController(GlobalControlProcess):


    def __init__(self, stublp):
        GlobalControlProcess.__init__(self)
        self.id = GlobalControlProcess.CONTROLLER_ID
        self.drones = []
        self.stublp = stublp
        self.gvtTokenRing = [self.stublp.LPID]
        self.gvt = 0

    def __call__(self):
        self.run()

    def addDrone(self, drone):
        self.drones.append(drone)
        self.gvtTokenRing.append(drone.LPID)

    def run(self):

        #Start the timer
        start_time = time.time()        

        # Self
        print('Stub Controller running')

        # Get the message queue objects from Pyro    
        nameserver = Pyro4.locateNS()
        
        controllerInQ_uri = nameserver.lookup('inputqueue.stubcontroller')
        self.inputQueue = Pyro4.Proxy(controllerInQ_uri)
        
        stublpInQ_uri = nameserver.lookup('inputqueue.stublp')
        self.stublpInQ = Pyro4.Proxy(stublpInQ_uri)        
        
        droneInQs_uri = nameserver.lookup('inputqueue.stubdrones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
         
        while True:
            
            time.sleep(10)
            
            # GVT: Trigger round for cut C1 (Stup LP is first LP in token ring)
            print 'Controller sending cut C1 token to first LP'
            self.stublpInQ.addMessage(Message(1, GVTControlMessageData(self.gvtTokenRing), GlobalControlProcess.CONTROLLER_ID, LogicalProcess.STUBLP_ID, -1))
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
                self.stublpInQ.addMessage(Message(1, GVTValue(gvt), GlobalControlProcess.CONTROLLER_ID, LogicalProcess.STUBLP_ID, -1))                  
            else:
                # GVT: Trigger round for cut C2
                print 'Controller sending cut C2 token to first LP'
                sys.stdout.flush()
                self.stublpInQ.addMessage(msg)
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
                self.stublpInQ.addMessage(Message(1, GVTValue(gvt), GlobalControlProcess.CONTROLLER_ID, LogicalProcess.STUBLP_ID, -1))                 
                sys.stdout.flush()                
            break

        print "Time elapsed: ", time.time() - start_time, "s"

