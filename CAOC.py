import sys, time
from HMINT import *
from multiprocessing import Queue, Lock
from LogicalProcess import *
from MessageManager import *

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
        
        # connect with Queue manager        
        qclient = self.QueueServerClient(self.REMOTE_HOST, self.PORT, self.AUTHKEY)
        
        # Get the message queue objects from the client
        inputQueues = qclient.get_queues()
        controllerInQ = inputQueues.get("controller")
        imintInQ = inputQueues.get("imint")
        inputQueue = inputQueues.get("caoc")
        droneInQs = inputQueues.get('drones')        
        
        
