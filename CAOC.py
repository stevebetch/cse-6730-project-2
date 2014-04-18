import sys, time
from HMINT import *
from multiprocessing import Queue, Lock
from LogicalProcess import *
from Message import *
from state import *
import Pyro4

class CAOC (LogicalProcess):
    "Central Air Operations Center"

    # Instance Variable List
    # id: Unique ID for this object
    # hmint: HMINT component supplying target info
    # priorityQueue: priority queue of available targets
    # controller: the simulation executive
    # drones: list of existing drones, with their status data
    # heuristic: identifies which heuristic for target-drone assignments is being used

    # Initialize CAOC
    # Input: numDrones=total number of drones for this sim run, heuristicNum=1,2, or 3 (naive, local, or timer heuristic)
    # Output: Initializes CAOC logical process
    # Description: Intialization of parameters that control target prioritization and drone-target assignments   
    def __init__(self, numDrones, heuristicNum):
        LogicalProcess.__init__(self)
        self.id = 'CAOC'
        self.priorityQueue = []
        self.drones=[]
        for i in range(numDrones):
            self.drones.insert(i,["Idle",0])
        self.heuristic=heuristicNum
 
    # Call function
    def __call__(self):
        self.run()

    # Save State
    # Input: None
    # Output: Saves current state of CAOC logical process
    # Description: Saves all parameters needed to describe state of LP, including HMINT state variables
    def saveState(self):
        saver=CAOCState(self)
        self.stateQueue.append(saver)

    def restoreState(self,timeStamp):
        print 'restoring to last state stored <= %d' % (timestamp)
        index=0
        for i in range(len(self.stateQueue)-1,-1,-1):
            if(timeStamp>=self.stateQueue[i].key):
                index=i
                break
        self.Restore(self.stateQueue(index))

    def Restore(obj):
        self.localTime=obj.localTime
        self.id=obj.id
        self.priorityQueue=obj.priorityQueue
        self.drones=obj.drones
        self.heuristic=obj.heuristic
        self.hmint=obj.hmint
        self.hmint.numTargets=obj.hmint.numTargets
        self.hmint.count=obj.hmint.count
        self.hmint.msgTimeStamp=obj.hmint.msgTimeStamp
        self.hmint.mapNodes=obj.hmint.mapNodes
        self.hmint.randSeed=obj.hmint.randSeed

    # Set Current Time
    # Input: time
    # Output: input queue time updated
    # Description: Changes current time in input queue to determine which messages to take out of the queue  
    def setInputQueueCurrentTime(self, time):
        self.inputQueue.setCurrentTime(time)

    # Set HMINT
    # Input: HMINT object
    # Output: Links HMINT object to CAOC
    # Description: Allows CAOC to access required info from HMINT   
    def setHMINT(self, hmint):
        self.hmint = hmint

    # Add Target
    # Input: Target Data data structure from Message data structure (see Message.py for documentation)
    # Output: Adds target to priority queue or assigns target to drone
    # Description: Regardless of heuristic, if all the drones are busy, the target is added to the queue in prioirity order
    #    Naive heuristic: if the queue is empty and there are idle drones, the target is assigned to the lowest-id drone
    #    Local and Timer heuristics: if the queue is empty and there are idles drones, the target is assigned to the closest drone
    def addTarget(self, targetData):
        # Check if the queue is empty
        if len(self.priorityQueue)==0:
            # Check which target assignment heruristic is in use
            if self.heuristic==1:
                # If the queue is empty and there is an idle drone, send it the incoming target assignment
                for i in range(len(self.drones)):
                    if self.drones[i][0]=="Idle":
                        newTgtMsg=Message(2,targetData,self.id,i,self.localTime)
                        self.sendMessage(newTgtMsg)    
                        break
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                else:
                    self.priorityQueue.insert(0,targetData)
                    print('CAOC Added target to priority queue')
            # Check which target assignment heruristic is in use
            elif self.heuristic==2:
                # Determine distance of target from idle drones
                tgtLocation=targetData[6] #x,y coords
                indexCloseDrone=0
                minDist=999999 #arbitrarily large cut-off
                for i in range(len(self.drones)):
                    droneLocation=self.drones[i][2]
                    dist=sqrt((tgtLocation[0]-droneLocation[0])^2+(tgtLocation[1]-droneLocation[1])^2)
                    if dist<minDist and self.drones[i][0]=="Idle":
                        minDist=dist
                        indexCloseDrone=i   
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                if minDist==999999:
                    self.priorityQueue.insert(0,targetData)
                    print('CAOC Added target to priority queue')
                # If the queue is empty and there are idle drones, send the nearest drone the incoming target assignment   
                else:
                    newTgtMsg=Message(2,targetData,self.id,indexCloseDrone,self.localTime)
                    self.sendMessage(newTgtMsg)
            elif self.heuristic==3:
                # Adjust tgt priority be intel value/goal track time if the tgt has no track attempts
                if msg[1][9]==0:
                    msg[1][2]=msg[1][1]/msg[1][7]   
                # Determine distance of target from idle drones
                tgtLocation=targetData[6] #x,y coords
                indexCloseDrone=0
                minDist=999999
                for i in range(len(self.drones)):
                    droneLocation=self.drones[i][2]
                    dist=sqrt((tgtLocation[0]-droneLocation[0])^2+(tgtLocation[1]-droneLocation[1])^2)
                    if dist<minDist and self.drones[i][0]=="Idle":
                        minDist=dist
                        indexCloseDrone=i   
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                if minDist==999999:
                    self.priorityQueue.insert(0,targetData)
                    print('CAOC Added target to priority queue')
                # If the queue is empty and there are idle drones, send the nearest drone the incoming target assignment   
                else:
                    newTgtMsg=Message(2,targetData,self.id,indexCloseDrone,self.localTime)
                    self.sendMessage(newTgtMsg)                
        # If the queue is not empty (implying all drones are busy), put the target assignment in the queue in order
        else:
            for i in range(len(self.priorityQueue)):
                if targetData[2]<self.priorityQueue[i][2]:
                    self.priorityQueue.insert(i,targetData)
                    break
            print('CAOC Added target to priority queue')

    # Get Priority Queue
    # Input: None
    # Output: Priority Queue (list)
    # Description: Access priority queue     
    def getPriorityQueue(self):
        return self.priorityQueue

    # Handle Message 
    # Input: Message data structure (see Message.py for documentation)
    # Output: Updates drone status, adds target to priority queue, or assigns target to drone [or TBD for msg type 1]
    # Description: Handles message based on message type
    #    Msg Type 1: [TBD]
    #    Msg Type 2: Calls addTarget function for Target Data attribute of input Message
    #    Msg Type 3: Updates drone status list, if the message indicates the drone is idle and there are target assignments in the queue
    #        Naive heuristic: Top priority target is assigned to drone
    #        Local or timer heuristic: Nearest target is assigned to drone (out of priority order)
    def subclassHandleMessage(self, msg):
        # determine message type and process accordingly
        if msg.msgType==1:
            # TBD
            pass
        elif msg.msgType==2:
            # Start the add target process with the target data of the message
            self.addTarget(msg[1])
        elif msg.msgType==3:
            # Update drone status list
            self.drones[msg.data[0]]=[msg.data[1],msg.data[2]]
            # Check which target assignment heruristic is in use
            if self.heuristic==1:
                # If the drone is idle and there are target assignments in the queue, assign that drone a target
                if (self.drones[msg.data[0]][1]=="Idle") and (len(self.priorityQueue)!=0):
                    newTgtData=self.priorityQueue.pop()
                    newTgtMsg=Message(2,newTgtData,self.id,msg.data[0],self.localTime)
                    self.sendMessage(newTgtMsg) 
            # Check which target assignment heruristic is in use
            elif self.heuristic==2 or self.heuristic==3:
                # If the drone is idle and there are target assignments in the queue, assign that drone the nearest target
                if (self.drones[msg.data[0]][1]=="Idle") and (len(self.priorityQueue)!=0):
                    droneLocation=self.drones[msg.data[0]][2] #x,y coords
                    indexCloseTgt=0
                    minDist=999999
                    for i in range(len(self.priorityQueue)):
                        tgtLocation=self.prioirityQueue[i][2]
                        dist=sqrt((tgtLocation[0]-droneLocation[0])^2+(tgtLocation[1]-droneLocation[1])^2)
                        if dist<minDist:
                            minDist=dist
                            indexCloseTgt=i   
                    newTgtData=self.priorityQueue.pop(indexCloseTgt)
                    newTgtMsg=Message(2,newTgtData,self.id,msg.data[0],self.localTime)
                    self.sendMessage(newTgtMsg) 

    # Run
    # Input: None
    # Output: Starts associated objects and queues
    # Description: Save state, start queues, start linked HMINT      
    def run(self):
        print('CAOC/HMINT Running')

        self.saveState()

        # Get the message queue objects from Pyro    
        nameserver = Pyro4.locateNS()
        controllerInQ_uri = nameserver.lookup('inputqueue.controller')
        self.controllerInQ = Pyro4.Proxy(controllerInQ_uri)
        caocInQ_uri = nameserver.lookup('inputqueue.caoc')
        self.inputQueue = Pyro4.Proxy(caocInQ_uri)
        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        self.imintInQ = Pyro4.Proxy(imintInQ_uri)
        droneInQs_uri = nameserver.lookup('inputqueue.drones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
        tgtPriQ_uri = nameserver.lookup('priorityqueue.targets')
        self.tgtPriQ = Pyro4.Proxy(tgtPriQ_uri)
        
        self.hmint.start()

        ## Mark: Test code can be removed
        #self.tgtPriQ.put('target 1')
        #self.tgtPriQ.put('target 2')
        #self.tgtPriQ.put('target 3')
        #t=[1,85,85,"Vehicle",0.8,1.2,[3,10],30,0,0]
        #u=[2,95,95,"Vehicle",0.8,1.2,[3,10],30,0,0]
        #self.priorityQueue=[t]
        #self.addTarget(u)
        #print 'CAOC Priority Queue: '
        #print self.priorityQueue

        # Event loop
        #while True:
            #msg = self.inputQueue.getNextMessage()
            #print 'CAOC iteration'
            #if msg:
                #self.handleMessage(msg)