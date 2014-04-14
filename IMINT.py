import sys, time
import Pyro4
from LogicalProcess import *

class IMINT (LogicalProcess):

    # instance variable list
    #id - unique id for component

    def __init__(self):
        LogicalProcess.__init__(self)
        self.id = 'IMINT'

    def __call__(self):
        self.run()
        
    def saveState(self):
        print 'Saving current state'
    
    def restoreState(self, timestamp):
        print 'restoring to last state stored <= %d' % (timestamp)
        #

    def subclassHandleMessage(self, msg):
        # determine message type and process accordingly
        # should deal only with type 2 messages
        #    receiving target complete messages and determining whether complete
        #       Threshold for good enough completion?
        #    sending target reaccomplish messages to CAOC as needed
        #       This requires updating priority, probably as a percentage of the original priority, for example 10% increase: priority of 50 becomes 55
        msg.printData(1)
        # Mark: below line for test only
        #self.sendMessage(Message(1, ['Data1'], 'IMINT', 'CAOC', 9))

    def run(self):

        print('IMINT Running')
        
        self.saveState()

        # Get the message queue objects from Pyro    
        nameserver = Pyro4.locateNS()
        #controllerInQ_uri = nameserver.lookup('inputqueue.controller')
        #self.controllerInQ = Pyro4.Proxy(controllerInQ_uri)
        caocInQ_uri = nameserver.lookup('inputqueue.caoc')
        self.caocInQ = Pyro4.Proxy(caocInQ_uri)        
        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        self.inputQueue = Pyro4.Proxy(imintInQ_uri)
        #droneInQs_uri = nameserver.lookup('inputqueue.drones')
        #self.droneInQs = Pyro4.Proxy(droneInQs_uri)

        # Event loop iteration
        while True:
            print 'IMINT loop iteration'
            msg = self.getNextMessage()
            print msg
            if msg:
                self.handleMessage(msg)
            time.sleep(0.05)
                
