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
    

    def __init__(self, numDrones, heuristicNum):
        LogicalProcess.__init__(self)
        self.id = 'CAOC'
        self.priorityQueue = Queue()
        self.drones=[]
        for i in range(0,numDrones):
            self.drones.insert(i,["Idle",0])
        self.heuristic=heuristicNum
     
    def __call__(self):
        self.run()
        
    def setController(self, controller):
        self.controller = controller
        
    def setHMINT(self, hmint):
        self.hmint = hmint
        
    def addTarget(self, targetData):
        if self.priorityQueue.empty():
            for i in range(0,len(self.drones)):
                if self.drones[i][0]=="Idle":
                    # If the queue is empty and there is an idle drone, send it a target assignment
                    newTgt=Message(2,targetData,self.id,i,t_Now)
                    # SEND MESSAGE - how to do this?
                    break
            else:
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                self.priority.put(targetData)
        else:
            # If the queue is not empty (implying all drones are busy), put the target assignment in the queue
            priority = self.getPriority(targetData)
            #self.priorityQueue.put(priority, target)
            self.priorityQueue.put(targetData)
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
                # Start the add target process with the target data of the message
                self.addTarget(msg[1])
            elif msg.msgType==3:
                # Update drone status list
                self.drones[msg.data[0]]=[msg.data[1],msg.data[2]]
                # If the drone is idle and there are target assignments in the queue, assign that drone a target
                if (self.drones[msg.data[0]][1]=="Idle") and not(self.priorityQueue.empty()):
                    newTgtData=self.priorityQueue.get()[1]
                    newTgt=Message(getNextMessageID(),2,newTgtData,self.id,msg.data[0],t_Now)
            pass    

    def run(self):
        print('CAOC/HMINT Running')
        self.hmint.start()
        
        

# DEBUGGING

status_data=[1,"Busy",13]
status_msg=Message(3,status_data,5,1,11)
print status_msg.data[0]
c=CAOC(2,1)
c.handleMessage(status_msg)
print c.drones
print c.priorityQueue.get()