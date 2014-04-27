import sys
from LogicalProcess import *
from state import *
from Message import *
import Pyro4

class StubDrone (LogicalProcess):

    # instance argument list
    #id - unique id of drone
    #droneType - descriptive

    def __init__(self, uid):
        self.uid = uid
        LogicalProcess.__init__(self)
    
    def __call__(self):
        self.run()
        
    def getCurrentState(self):
        return None        
    
    def run(self):
        # Begin process of selecting target from CAOC priority queue, tracking, check when refueling needed, etc.
        print('Stub Drone process running')
        self.saveState()
       
        # Get the message queue objects from Pyro
        nameserver = Pyro4.locateNS()
        LPIDs = []
        
        self.imintInQ = None
        self.hmintInQ = None
        self.caocInQ = None
        
        controllerInQ_uri = nameserver.lookup('inputqueue.stubcontroller')
        self.controllerInQ = Pyro4.Proxy(controllerInQ_uri)
        
        stublpInQ_uri = nameserver.lookup('inputqueue.stublp')
        self.stublpInQ = Pyro4.Proxy(stublpInQ_uri)
        LPIDs.append(self.stublpInQ.LPID)        
        
        droneInQs_uri = nameserver.lookup('inputqueue.stubdrones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
        LPIDs.extend(self.droneInQs.getLPIDs())
        
        self.initGVTCounts(LPIDs)  
        
        # GVT Test 3
        msg8 = Message(2, 'Data8', 0, LogicalProcess.STUBLP_ID, 8)
        self.sendMessage(msg8)        
        
        # Event loop iteration
        count = 10
        while True:
            time.sleep(2)
            print 'Stub drone %d event loop iteration' % (self.uid)
            msg = self.getNextMessage()
            if msg:
                self.handleMessage(msg)
            sys.stdout.flush()
            
    
    def subclassHandleMessage(self, msg):
        if(msg.msgType==1):
            print 'subclassHandleMessage: message type 1'        
        elif(msg.msgType==2):
            print 'subclassHandleMessage type 2:', msg.data
        elif(msg.msgType==3):
            print 'subclassHandleMessage type 3:', msg.data          
        sys.stdout.flush()
        

    def saveState(self):
        print 'drone %d saving state' % self.uid
        self.stateQueue.append(StubState(self.localTime))

    def restoreState(self,timestamp):
        print 'drone %d restoring to last state stored <= %d' % (self.uid, timestamp)
          