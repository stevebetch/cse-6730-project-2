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
from Message import *


class StubController(GlobalControlProcess):


    def __init__(self, stublp):
        GlobalControlProcess.__init__(self)
        self.id = GlobalControlProcess.CONTROLLER_ID
        self.drones = []
        self.stublp = stublp
        self.gvtTokenRing = [self.stublp.LPID]
        print 'init: gvtTokenRing:',self.gvtTokenRing
        self.gvt = 0

    def __call__(self):
        self.run()

    def addDrone(self, drone):
        self.drones.append(drone)
        self.gvtTokenRing.append(drone.LPID)
        print 'addDrone: gvtTokenRing:',self.gvtTokenRing

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
        
        loopInQs_uri = nameserver.lookup('inL.loop')
        self.Loopcont = Pyro4.Proxy(loopInQs_uri)
        
        while (self.Loopcont.getCon()==1):
        
            for i in range(1,11):
                time.sleep(1)
                if(self.Loopcont.getCon()==0):
                    break
            
            # GVT: Trigger round for cut C1 (Stup LP is first LP in token ring)
            if(debug==1):
                print 'Controller sending cut C1 token to first LP'
                print self.gvtTokenRing
            self.stublpInQ.addMessage(Message(1, GVTControlMessageData(self.gvtTokenRing), GlobalControlProcess.CONTROLLER_ID, LogicalProcess.STUBLP_ID, -1))
            msg = None
            if(debug==1):
                print 'Controller waiting for cut C1 token'
                sys.stdout.flush()
            while True:
                if(self.Loopcont.getCon()==0):
                    break
                time.sleep(0)
                msg = self.inputQueue.getNextMessage()
                if not(msg is None):
                    if isinstance(msg.data, GVTControlMessageData):
                        break
            if(self.Loopcont.getCon()==0):
                break
            if(debug==1):
                print 'Controller received GVT control token back from LPs (Cut C1)'
                sys.stdout.flush()
        
            count = 0
            for i in msg.data.counts:
                if(debug==1):
                    print 'GVT counts[%d] = %d (after cut C1)' % (i, msg.data.counts[i])
                count += msg.data.counts[i]
                
            if(debug==1):
                print 'Total counts in GVT = %d (after cut C1)' % (count)
            if count <= 0:
                # GVT: Send GVT value to all LPs
                if(debug==1):
                    print 'Controller sending GVT value to first LP'
                    sys.stdout.flush()
                gvt = min(msg.data.tMin, msg.data.tRed)
                self.stublpInQ.addMessage(Message(1, GVTValue(gvt), GlobalControlProcess.CONTROLLER_ID, LogicalProcess.STUBLP_ID, -1))                  
            else:
                # GVT: Trigger round for cut C2
                if(debug==1):
                    print 'Controller sending cut C2 token to first LP'
                    sys.stdout.flush()
                self.stublpInQ.addMessage(msg)
                if(debug==1):
                    print 'Controller waiting for cut C2 token'
                    sys.stdout.flush()
                while True:
                    if(self.Loopcont.getCon()==0):
                        break
                    time.sleep(0)                    
                    msg = self.inputQueue.getNextMessage()
                    if not(msg is None):
                        if isinstance(msg.data, GVTControlMessageData):
                            break
                if(self.Loopcont.getCon()==0):
                    break
                if(debug==1):
                    print 'Controller received GVT control token back from LPs (Cut C2)'
                count = 0
                for i in msg.data.counts:
                    if(debug==1):
                        print 'GVT counts[%d] = %d (after cut C2)' % (i, msg.data.counts[i])
                    count += msg.data.counts[i]
                if(debug==1):
                    print 'Total counts in GVT = %d (after cut C2)' % (count)
                # GVT: Send GVT value to all LPs
                if(debug==1):
                    print 'Controller sending GVT value to first LP'
                    sys.stdout.flush()
                gvt = min(msg.data.tMin, msg.data.tRed)
                if(debug==1):
                    print 'GVT value is %d' % (gvt)
                self.stublpInQ.addMessage(Message(1, GVTValue(gvt), GlobalControlProcess.CONTROLLER_ID, LogicalProcess.STUBLP_ID, -1))                 
#                sys.stdout.flush()                
            break
        
        print "Time elapsed: ", time.time() - start_time, "s"

