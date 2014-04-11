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
            self.drones.insert(i,["Idle",0])
        
    def __call__(self):
        self.run()
        
    def setController(self, controller):
        self.controller = controller
        
    def setHMINT(self, hmint):
        self.hmint = hmint
        
    def addTarget(self, target):
        switch=0
        for i in range(0,len(self.drones)):
            if self.drones[i][0]=="Idle":
                # send message to drone LP
                switch=1
                tgtData=[target.data[0],target.data[1],target.data[2],target.data[3],target.data[4],target.data[5],target.data[6],target.data[7],target.data[9]]
                newTgt=Message(getNextMessageID(),2,tgtData,self.id,i,t_Now)
                # SEND MESSAGE - how to do this?
                break
        if switch==0:    
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
                if self.drones[msg.data[0]][1]=="Idle":
                    #tgtData=priorityQueue.pop(0)
                    newTgt=Message(getNextMessageID(),2,tgtData,self.id,msg.data[0],t_Now)
            pass    

    def run(self):
        print('CAOC/HMINT Running')
        self.hmint.start()
        
        

# DEBUGGING
status_data=[1,"Busy",13]
status_msg=Message(1,3,status_data,5,1,11)
print status_msg.data[0]
c=CAOC(2)
c.handleMessage(status_msg)
print c.drones