import sys, time
import Pyro4
from LogicalProcess import *
from state import StubState
from multiprocessing import Queue, Lock
from Message import *

class StubLP (LogicalProcess):

    def __init__(self):
        LogicalProcess.__init__(self)
        self.id = LogicalProcess.STUBLP_ID

    def __call__(self):
        self.run()
    
    def saveState(self):
        print 'Saving current StubLP state'
        self.stateQueue.append(StubState(self.localTime))
       
    def restoreState(self, timestamp):
        print 'restoring to last StubLP state stored <= %d' % (timestamp)
        
    def subclassHandleMessage(self, msg):
        if(msg.msgType==1):
            print 'subclassHandleMessage: message type 1'        
        elif(msg.msgType==2):
            print 'subclassHandleMessage type 2:', msg.data
        elif(msg.msgType==3):
            print 'subclassHandleMessage type 3:', msg.data          
        sys.stdout.flush()

    def run(self):

        print('StubLP Running')
        
        self.saveState()

        # Get the message queue objects from Pyro    
        nameserver = Pyro4.locateNS()
        LPIDs = []
        
        self.imintInQ = None
        self.hmintInQ = None
        self.caocInQ = None        
        
        controllerInQ_uri = nameserver.lookup('inputqueue.stubcontroller')
        self.inputQueue = Pyro4.Proxy(controllerInQ_uri)        
        
        stublpInQ_uri = nameserver.lookup('inputqueue.stublp')
        self.inputQueue = Pyro4.Proxy(stublpInQ_uri)
        self.stublpInQ = None
        LPIDs.append(self.inputQueue.LPID)
        
        droneInQs_uri = nameserver.lookup('inputqueue.stubdrones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
        LPIDs.extend(self.droneInQs.getLPIDs())
        
        self.initGVTCounts(LPIDs)

        #
        # Test messages
        #
        
        # GVT tests 2 and 3: 3 msgs to same drone
        msg3 = Message(2, 'Data3', LogicalProcess.STUBLP_ID, 0, 3)
        msg4 = Message(2, 'Data4', LogicalProcess.STUBLP_ID, 0, 4)
        msg7 = Message(2, 'Data7', LogicalProcess.STUBLP_ID, 0, 7)
        self.sendMessage(msg3)
        self.sendMessage(msg4)
        self.sendMessage(msg7)
        
        ## Event loop iteration
        while True:
            print 'STUB LP loop iteration'
            msg = self.getNextMessage()
            if msg:
                self.handleMessage(msg)
            time.sleep(2)
            sys.stdout.flush()

