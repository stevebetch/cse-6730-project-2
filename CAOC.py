import sys, time
from HMINT import *
from multiprocessing import Queue
from LogicalProcess import *

class CAOC (LogicalProcess):
    "Central Air Operations Center"
    
    # instance variable list
    #hmint
    #priorityQueue
    #controller
    
    def __init__(self):
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
    
    def getNextTarget(self):
        return self.priorityQueue.get()
        
    
    def handleMessage(self, msg):
            # determine message type and process accordingly
            # IS IT WORKING
            pass    

    def run(self):
        print('CAOC/HMINT Running')
        self.hmint.start()
        
        
