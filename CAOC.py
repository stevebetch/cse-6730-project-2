import sys, time
from HMINT import *
from multiprocessing import Queue, Lock
from LogicalProcess import *
from Message import *

class CAOC (LogicalProcess):
    "Central Air Operations Center"
    
    # instance variable list
    #id - Unique ID for this object
    #hmint - HMINT component supplying target info
    #priorityQueue - queue of available targets
    #controller - the simulation executive
    

    def __init__(self, numDrones):
        LogicalProcess.__init__(self)
        self.id = 'CAOC'
        self.priorityQueue = Queue()
        self.drones=[]
        for i in range(0,numDrones):
            self.drones.insert(i,[0,0])
        
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
            # do we need another function here to determine when to process the message?

            # determine message type and process accordingly
            if msg.msgType==1:
                1==1 #placeholder
            elif msg.msgType==2:
                self.addTarget(msg)
            elif msg.msgType==3:
                self.drones[msg.data[0]]=[msg.data[1],msg.data[2]]
            pass    

    def run(self):
        print('CAOC/HMINT Running')
        self.hmint.start()
        
        

# DEBUGGING
status_data=[3,"Idle",13]
status_msg=Message(1,3,status_data,5,1,11)
c=CAOC(2)
print c.drones