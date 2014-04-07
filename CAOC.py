import sys
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
        
    def setController(self, controller):
        self.controller = controller
        
    def setHMINT(self, hmint):
        self.hmint = hmint

    # Runs CAOC process (incl HMINT)
    def run(self):
        hmint.start()
        
    def addTarget(self, target):
        priority = self.getPriority(target)
        self.priorityQueue.put(priority, target)
    
    def getPriority(self, target):
        # generate priority
        pass
    
    def getPriorityQueue(self):
        return self.priorityQueue
    
    def getNextTarget(self, neighborhood):
        return self.priorityQueue.get(neighborhood)
    
    def handleMessage(self, msg):
            # determine message type and process accordingly
            # IS IT WORKING
            pass    

