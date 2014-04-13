import sys, time
from HMINT import *
from multiprocessing import Queue, Lock
from LogicalProcess import *
from Message import *
import Pyro4

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
        self.priorityQueue = []
        self.drones=[]
        for i in range(numDrones):
            self.drones.insert(i,["Idle",0])
        self.heuristic=heuristicNum

    def __call__(self):
        self.run()

    def getCurrentState(self):
        return None 

    def setInputQueueCurrentTime(self, time):
        self.inputQueue.setCurrentTime(time)

    def setHMINT(self, hmint):
        self.hmint = hmint

    def addTarget(self, targetData):
        if len(self.priorityQueue):
            # Check which target assignment heruristic is in use
            if self.heuristic==1:
                # If the queue is empty and there is an idle drone, send it the incoming target assignment
                for i in range(len(self.drones)):
                    if self.drones[i][0]=="Idle":
                        newTgt=Message(2,targetData,self.id,i,self.localTime)
                        # SEND MESSAGE - how to do this?
                        break
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                else:
                    self.priorityQueue.insert(0,targetData)
            # Check which target assignment heruristic is in use
            elif self.heuristic==2 or self.heuristic==3:
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
                # If the queue is empty and there are idle drones, send the nearest drone the incoming target assignment   
                else:
                    newTgt=Message(2,targetData,self.id,indexCloseDrone,self.localTime)
                    # SEND MESSAGE - how to do this?
        else:
            # If the queue is not empty (implying all drones are busy), put the target assignment in the queue
            for i in range(len(self.priorityQueue)):
                if targetData[2]<self.priorityQueue[i][2]:
                    self.priorityQueue.insert(i,targetData)
                    break
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
        if msg.msgType==1:
            1==1 #placeholder
            print msg
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
                    newTgt=Message(getNextMessageID(),2,newTgtData,self.id,msg.data[0],self.localTime)
            # Check which target assignment heruristic is in use
            elif self.heuristic==2 or self.heuristic==3:
                # If the drone is idle and there are target assignments in the queue, assign that drone a nearby target
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
                    newTgt=Message(getNextMessageID(),2,newTgtData,self.id,msg.data[0],self.localTime)   

    def run(self):
        print('CAOC/HMINT Running')
        self.hmint.start()

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

        # Mark: Test code can be removed
        self.tgtPriQ.put('target 1')
        self.tgtPriQ.put('target 2')
        self.tgtPriQ.put('target 3')
        t=[1,85,85,"Vehicle",0.8,1.2,[3,10],30,0,0]
        u=[2,95,95,"Vehicle",0.8,1.2,[3,10],30,0,0]
        self.priorityQueue=[t,t,t,t,t,t,t,t,t]
        self.addTarget(u)
        #print 'CAOC: ' + self.inputQueue.getNextMessage()
        print 'CAOC Priority Queue: '
        print self.priorityQueue

        while True:
            msg = self.inputQueue.getNextMessage()
            print 'CAOC iteration'
            if msg:
                self.handleMessage(msg)
                break

# DEBUGGING
def main():
    status_data=[1,"Busy",13]
    status_msg=Message(3,status_data,5,1,11)
    print status_msg.data[0]
    c=CAOC(2,1)
    c.handleMessage(status_msg)
    print c.drones

if __name__ == '__main__':
    main()