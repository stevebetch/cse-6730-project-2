import sys, time
from HMINT import *
from multiprocessing import Queue, Lock
from LogicalProcess import *
import Pyro4

class CAOC (LogicalProcess):
    "Central Air Operations Center"
    
    # instance variable list
    #id - Unique ID for this object
    #hmint - HMINT component supplying target info
    #priorityQueue - queue of available targets
    #controller - the simulation executive
    
    def __init__(self):
        self.id = 'CAOC'
        LogicalProcess.__init__(self)
        self.priorityQueue = Queue()
        
    def __call__(self):
        self.run()
        
    def setController(self, controller):
        self.controller = controller
        
    def setHMINT(self, hmint):
        self.hmint = hmint
        
    def addTarget(self, target):
        priority = self.getPriority(target)
        #self.priorityQueue.put(priority, target)
        self.priorityQueue.put(target)
        print('CAOC Added target to priority queue')
    
    def getPriority(self, target):
        # generate priority
        pass
    
    def getPriorityQueue(self):
        return self.priorityQueue
    
    def getNextTarget(self, lock, location, radius):
        lock.aquire
        target =  self.priorityQueue.get()
        lock.release
        return target
    
    def handleMessage(self, msg):
            # determine message type and process accordingly
            pass    

    def run(self):
        print('CAOC/HMINT Running')
        self.hmint.start()
        
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
        tgtPriQ_uri = nameserver.lookup('priorityqueue.targets')
        self.tgtPriQ = Pyro4.Proxy(tgtPriQ_uri) 
        
        self.tgtPriQ.put('target 1')
        self.tgtPriQ.put('target 2')
        self.tgtPriQ.put('target 3')
        
        print 'CAOC: ' + self.caocInQ.get()
