import sys, time
from math import *
from LogicalProcess import *
from HMINT import *
from multiprocessing import Queue, Lock
from Message import *
from nodes import *
from Map import *
from state import *
import Pyro4

class CAOC (LogicalProcess):
    "Central Air Operations Center"

    # Instance Variable List
    # id: Unique ID for this object
    # priorityQueue: priority queue of available targets
    # controller: the simulation executive
    # drones: list of existing drones, with their status data
    # heuristic: identifies which heuristic for target-drone assignments is being used

    # Initialize CAOC
    # Input: numDrones=total number of drones for this sim run, heuristicNum=1,2, or 3 (naive, local, or timer heuristic)
    # Output: Initializes CAOC logical process
    # Description: Intialization of parameters that control target prioritization and drone-target assignments   
    def __init__(self, numDrones, heuristicNum, node):
        LogicalProcess.__init__(self)
        self.id = LogicalProcess.CAOC_ID
        self.priorityQueue = []
        self.drones=[]
        for i in range(numDrones):
            self.drones.insert(i,["Busy",node])
        self.heuristic=heuristicNum

    # Call function
    def __call__(self):
        self.run()

    # Save State
    # Input: None
    # Output: Saves current state of CAOC logical process
    # Description: Saves all parameters needed to describe state of LP
    def saveState(self):
        if(debug==1):
            print 'Saving current CAOC state'
        saver=CAOCState(self)
        self.stateQueue.append(saver)

    def restoreState(self,timestamp):
        if(debug==1):
            print "restoring to last CAOC state stored <=",timestamp
#        index=0
#        for i in range(len(self.stateQueue)-1,-1,-1):
#            if(timestamp>=self.stateQueue[i].key):
#                index=i
#                break
#            else:
#                self.stateQueue.pop(i)
        if(debug==1):
            print "StateQueue times:"
        for i in self.stateQueue:
            if(debug==1):
                print i.key
        a=[]
        for i in self.stateQueue:
            if(timestamp>=i.key):
                ts = i.key
                index=i
                a.append(i)
        if(debug==1):
            print "Restoring state to timestamp:",ts
    
        self.restore(index)
        self.stateQueue=a
#        self.stateQueue.pop(len(self.stateQueue)-1)

    def restore(self,obj):
        self.localTime=obj.localTime
        self.id=obj.id
        self.priorityQueue=obj.priorityQueue
        self.drones=obj.drones
        self.heuristic=obj.heuristic

    # Set Current Time
    # Input: time
    # Output: input queue time updated
    # Description: Changes current time in input queue to determine which messages to take out of the queue  
    def setInputQueueCurrentTime(self, time):
        self.inputQueue.setCurrentTime(time)

    # Add Target
    # Input: Target Data data structure from Message data structure (see Message.py for documentation)
    # Output: Adds target to priority queue or assigns target to drone
    # Description: Regardless of heuristic, if all the drones are busy, the target is added to the queue in priority order
    #    Naive heuristic: if the queue is empty and there are idle drones, the target is assigned to the lowest-id drone
    #    Local and Timer heuristics: if the queue is empty and there are idles drones, the target is assigned to the closest drone
    def addTarget(self, targetData):
        # Check if the queue is empty
        if len(self.priorityQueue)==0:
            # Check which target assignment heruristic is in use
            if self.heuristic==1:
                # If the queue is empty and there is an idle drone, send it the incoming target assignment
                for i in range(len(self.drones)):
                    if self.drones[i][0]=='Idle':
                        newTgtMsg=Message(2,targetData,self.id,i,self.localTime) # drone ids start at 2
                        self.sendMessage(newTgtMsg)
                        self.drones[i][0]='Busy'
                        if(debug==1):
                            print 'sent message to idle drone:',i
                        break
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                else:
                    self.priorityQueue.insert(0,targetData)
                    if(debug==1):
                        print('CAOC Added target to priority queue')
            # Check which target assignment heruristic is in use
            elif self.heuristic==2:
                # Determine distance of target from idle drones
                tgtX=targetData[6].xpos #x coord
                tgtY=targetData[6].ypos #y coord
                indexCloseDrone=0
                minDist=999999 #arbitrarily large cut-off
                if(debug==1):
                    print self.drones
                for i in range(len(self.drones)):
                    droneX=self.drones[i][1].xpos
                    droneY=self.drones[i][1].ypos
                    dist=sqrt((tgtX-droneX)**2+(tgtY-droneY)**2)
                    if dist<minDist and self.drones[i][0]=="Idle":
                        minDist=dist
                        indexCloseDrone=i   
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                if minDist==999999:
                    self.priorityQueue.insert(0,targetData)
                    if(debug==1):
                        print('CAOC Added target to priority queue')
                # If the queue is empty and there are idle drones, send the nearest drone the incoming target assignment   
                else:
                    newTgtMsg=Message(2,targetData,self.id,indexCloseDrone,self.localTime) # drone ids start at 2
                    self.sendMessage(newTgtMsg)
                    self.drones[indexCloseDrone][0]='Busy'
            elif self.heuristic==3:
                # Adjust tgt priority be intel value/goal track time if the tgt has no track attempts
                if targetData[9]==0:
                    targetData[2]=targetData[1]/targetData[7]   
                # Determine distance of target from idle drones
                tgtX=targetData[6].xpos #x coord
                tgtY=targetData[6].ypos #y coord
                indexCloseDrone=0
                minDist=999999
                for i in range(len(self.drones)):
                    droneX=self.drones[i][1].xpos
                    droneY=self.drones[i][1].ypos
                    dist=sqrt((tgtX-droneX)**2+(tgtY-droneY)**2)
                    if dist<minDist and self.drones[i][0]=="Idle":
                        minDist=dist
                        indexCloseDrone=i   
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                if minDist==999999:
                    self.priorityQueue.insert(0,targetData)
                    if(debug==1):
                        print('CAOC Added target to priority queue')
                # If the queue is empty and there are idle drones, send the nearest drone the incoming target assignment   
                else:
                    newTgtMsg=Message(2,targetData,self.id,indexCloseDrone,self.localTime) # drone ids start at 0
                    self.sendMessage(newTgtMsg)
                    self.drones[indexCloseDrone][0]='Busy'
        # If the queue is not empty (implying all drones are busy), put the target assignment in the queue in order
        else:
            if self.heuristic==3:
                # Adjust tgt priority be intel value/goal track time if the tgt has no track attempts
                if targetData[9]==0:
                    targetData[2]=targetData[1]/targetData[7]
            # Put target data into priority queue in priority order
            if targetData[2]>=self.priorityQueue[len(self.priorityQueue)-1][2]:
                self.priorityQueue.append(targetData)
            else:
                for i in range(len(self.priorityQueue)):
                    if targetData[2]<self.priorityQueue[i][2]:
                        self.priorityQueue.insert(i,targetData)
                        break
            if(debug==1):
                print('CAOC Added target to priority queue')

    # Get Priority Queue
    # Input: None
    # Output: Priority Queue (list)
    # Description: Access priority queue     
    def getPriorityQueue(self):
        return self.priorityQueue
    
    def updateTargets(self, timestamp):
        
        # send request to HMINT for targets available as of self.localTime
        print 'CAOC: Sending target request for time %d to HMINT' % timestamp
        sys.stdout.flush()
        requestData = TargetRequest(timestamp)
        msg = Message(4, requestData, LogicalProcess.CAOC_ID, LogicalProcess.HMINT_ID, timestamp)
        self.sendMessage(msg) 
        
        # wait for response
        responseData = None
        while True:
            print 'CAOC: Waiting for target response from HMINT'
            sys.stdout.flush()
            time.sleep(1)
            if(self.Loopcont.getCon()==0):
                break
            msgs = self.inputQueue.getAllMessages()
            for msg in msgs:
                msg.printData(1)
                if msg.msgType == 5:
                    print 'CAOC: Received target response for time %d from HMINT' % self.localTime
                    sys.stdout.flush()
                    responseData = msg.data
                    self.inputQueue.removeByID(msg.id)
                    if msg.color == LPGVTData.WHITE:
                        self.gvtData.counts[self.LPID] -= 1
                        if(debug==1):
                            print 'LP %d recvd WHITE msg, rcvd count is now %d' % (self.LPID, self.gvtData.counts[self.LPID])                    
                    break
            if not(responseData is None):
                break
        
        # add targets
        if(self.Loopcont.getCon()==0):
            return
        for target in responseData.targetData:
            print 'CAOC: Adding target to priority queue:', target
            self.addTarget(target)        
            
        sys.stdout.flush()
                    

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
#       ss print "Handling message in CAOC, proirity queue length:", len(self.priorityQueue)
        if msg.msgType==1:
            # Control message handled in base class
            pass
        
        elif msg.msgType==5:
            print 'CAOC: Received target response from HMINT with %d targets' % len(msg.data.targetData)
            sys.stdout.flush()
            # Start the add target process with the target data of the message
            for target in msg.data.targetData:
                self.addTarget(target)
                
        elif msg.msgType==3:
            
            # Call HMINT to update target priority queue to current time
            self.updateTargets(msg.timestamp)
            if(self.Loopcont.getCon()==0):
                return
            # Update drone status list
            self.drones[msg.data[0]]=[msg.data[1],msg.data[2]]
            # Check which target assignment heruristic is in use
            if self.heuristic==1:
                # If the drone is idle and there are target assignments in the queue, assign that drone a target
                if (self.drones[msg.data[0]][0]=="Idle") and (len(self.priorityQueue)!=0):
                    newTgtData=self.priorityQueue.pop()
                    newTgtMsg=Message(2,newTgtData,self.id,msg.data[0],self.localTime)
                    self.sendMessage(newTgtMsg)
                    #newTgtMsg.printData()
                    self.drones[msg.data[0]][0]="Busy"
        
            # Check which target assignment heruristic is in use
            elif self.heuristic==2 or self.heuristic==3:
                # If the drone is idle and there are target assignments in the queue, assign that drone the nearest target
                if (self.drones[msg.data[0]][0]=="Idle") and (len(self.priorityQueue)!=0):
                    droneLocation=self.drones[msg.data[0]][1] #x,y coords
                    droneX=self.drones[msg.data[0]][1].xpos
                    droneY=self.drones[msg.data[0]][1].ypos                  
                    indexCloseTgt=0
                    minDist=999999
                    for i in range(len(self.priorityQueue)):
                        tgtX=self.priorityQueue[i][6].xpos #x coord
                        tgtY=self.priorityQueue[i][6].ypos #y coord                        
                        dist=sqrt((tgtX-droneX)**2+(tgtY-droneY)**2)
                        if dist<minDist:
                            minDist=dist
                            indexCloseTgt=i   
                    newTgtData=self.priorityQueue.pop(indexCloseTgt)
                    newTgtMsg=Message(2,newTgtData,self.id,msg.data[0],self.localTime)
                    self.sendMessage(newTgtMsg)
                    self.drones[msg.data[0]][0]="Busy"

    # Run
    # Input: None
    # Output: Starts associated objects and queues
    # Description: Save state, start queues      
    def run(self):

        print('CAOC Running')

        # Get the message queue objects from Pyro    
        nameserver = Pyro4.locateNS()
        LPIDs = []

        controllerInQ_uri = nameserver.lookup('inputqueue.controller')
        self.controllerInQ = Pyro4.Proxy(controllerInQ_uri)

        hmintInQ_uri = nameserver.lookup('inputqueue.hmint')
        self.hmintInQ = Pyro4.Proxy(hmintInQ_uri)
        LPIDs.append(self.hmintInQ.LPID)	

        caocInQ_uri = nameserver.lookup('inputqueue.caoc')
        self.inputQueue = Pyro4.Proxy(caocInQ_uri)
        self.caocInQ = None
        LPIDs.append(self.inputQueue.LPID)

        imintInQ_uri = nameserver.lookup('inputqueue.imint')
        self.imintInQ = Pyro4.Proxy(imintInQ_uri)
        LPIDs.append(self.imintInQ.LPID)

        droneInQs_uri = nameserver.lookup('inputqueue.drones')
        self.droneInQs = Pyro4.Proxy(droneInQs_uri)
        LPIDs.extend(self.droneInQs.getLPIDs())
        
        loopInQs_uri = nameserver.lookup('inL.loop')
        self.Loopcont = Pyro4.Proxy(loopInQs_uri)

        self.initGVTCounts(LPIDs)
        if(debug==1):
            print "Output contol value:",self.Loopcont.getCon()
#        self.saveState()

        # Event loop
        count=0
        while (self.Loopcont.getCon()):
            count+=1
#            time.sleep(.05)
            msg = self.getNextMessage()
            if(count%5000==0):
                print 'CAOC iteration. Local time', self.localTime
                for i in self.drones:
                    if(debug==1):
                        print "Drone status: ",i[0]
#            print 'CAOC Priority Queue: '
#            print self.priorityQueue
            if msg:
                self.handleMessage(msg)
                msg.printData(1)
            #sys.stdout.flush()
            
    
    
    
    # ############ TEST METHODS ############
    def testHandleMessage(self, msg):
        # determine message type and process accordingly
        if msg.msgType==1:
            # TBD
            pass
        elif msg.msgType==2:
            # Start the add target process with the target data of the message
            self.testAddTarget(msg.data)
        elif msg.msgType==3:
            # Update drone status list
            self.drones[msg.data[0]]=[msg.data[1],msg.data[2]]
            # Check which target assignment heruristic is in use
            if self.heuristic==1:
                # If the drone is idle and there are target assignments in the queue, assign that drone a target
                if (self.drones[msg.data[0]][0]=="Idle") and (len(self.priorityQueue)!=0):
                    newTgtData=self.priorityQueue.pop()
                    newTgtMsg=Message(2,newTgtData,self.id,msg.data[0],self.localTime)
                    #self.sendMessage(newTgtMsg)
                    if(debug==1):
                        print 'CAOC sending message: '
                        newTgtMsg.printData(1)
                    self.drones[msg.data[0]][0]="Busy"
        
            # Check which target assignment heruristic is in use
            elif self.heuristic==2 or self.heuristic==3:
                # If the drone is idle and there are target assignments in the queue, assign that drone the nearest target
                if (self.drones[msg.data[0]][0]=="Idle") and (len(self.priorityQueue)!=0):
                    droneLocation=self.drones[msg.data[0]][1] #x,y coords
                    droneX=self.drones[msg.data[0]][1].xpos
                    droneY=self.drones[msg.data[0]][1].ypos                  
                    indexCloseTgt=0
                    minDist=999999
                    for i in range(len(self.priorityQueue)):
                        tgtX=self.priorityQueue[i][6].xpos #x coord
                        tgtY=self.priorityQueue[i][6].ypos #y coord                        
                        dist=sqrt((tgtX-droneX)**2+(tgtY-droneY)**2)
                        if dist<minDist:
                            minDist=dist
                            indexCloseTgt=i   
                    newTgtData=self.priorityQueue.pop(indexCloseTgt)
                    newTgtMsg=Message(2,newTgtData,self.id,msg.data[0],self.localTime)
                    #self.sendMessage(newTgtMsg)
                    if(debug==1):
                        print 'CAOC sending message: '
                        newTgtMsg.printData(1)                    
                    self.drones[msg.data[0]][0]="Busy"


    # ############ TEST METHODS ############
    def testAddTarget(self, targetData):
        # Check if the queue is empty
        if len(self.priorityQueue)==0:
            # Check which target assignment heruristic is in use
            if self.heuristic==1:
                # If the queue is empty and there is an idle drone, send it the incoming target assignment
                for i in range(len(self.drones)):
                    if self.drones[i][0]=='Idle':
                        newTgtMsg=Message(2,targetData,self.id,i,self.localTime) 
                        #self.sendMessage(newTgtMsg)
                        if(debug==1):
                            print 'CAOC sending message: '
                            newTgtMsg.printData(1)                          
                        self.drones[i][0]='Busy'
                        break
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                else:
                    self.priorityQueue.insert(0,targetData)
            # Check which target assignment heruristic is in use
            elif self.heuristic==2:
                # Determine distance of target from idle drones
                tgtX=targetData[6].xpos #x coord
                tgtY=targetData[6].ypos #y coord
                indexCloseDrone=0
                minDist=999999 #arbitrarily large cut-off
                if(debug==1):
                    print self.drones
                for i in range(len(self.drones)):
                    droneX=self.drones[i][1].xpos
                    droneY=self.drones[i][1].ypos
                    dist=sqrt((tgtX-droneX)**2+(tgtY-droneY)**2)
                    if dist<minDist and self.drones[i][0]=="Idle":
                        minDist=dist
                        indexCloseDrone=i   
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                if minDist==999999:
                    self.priorityQueue.insert(0,targetData)
                # If the queue is empty and there are idle drones, send the nearest drone the incoming target assignment   
                else:
                    newTgtMsg=Message(2,targetData,self.id,indexCloseDrone,self.localTime)
                    #self.sendMessage(newTgtMsg)
                    print 'CAOC sending message: '
                    newTgtMsg.printData(1)                      
                    self.drones[indexCloseDrone][0]='Busy'
            elif self.heuristic==3:
                # Adjust tgt priority be intel value/goal track time if the tgt has no track attempts
                if targetData[9]==0:
                    targetData[2]=targetData[1]/targetData[7]   
                # Determine distance of target from idle drones
                tgtX=targetData[6].xpos #x coord
                tgtY=targetData[6].ypos #y coord
                indexCloseDrone=0
                minDist=999999
                for i in range(len(self.drones)):
                    droneX=self.drones[i][1].xpos
                    droneY=self.drones[i][1].ypos
                    dist=sqrt((tgtX-droneX)**2+(tgtY-droneY)**2)
                    if dist<minDist and self.drones[i][0]=="Idle":
                        minDist=dist
                        indexCloseDrone=i   
                # If the queue is empty and all drones are busy, put the target assignment in the queue
                if minDist==999999:
                    self.priorityQueue.insert(0,targetData)
                # If the queue is empty and there are idle drones, send the nearest drone the incoming target assignment   
                else:
                    newTgtMsg=Message(2,targetData,self.id,indexCloseDrone,self.localTime)
                    #self.sendMessage(newTgtMsg)
                    print 'CAOC sending message: '
                    newTgtMsg.printData(1)                      
                    self.drones[indexCloseDrone][0]='Busy'
        # If the queue is not empty (implying all drones are busy), put the target assignment in the queue in order
        else:
            if self.heuristic==3:
                # Adjust tgt priority be intel value/goal track time if the tgt has no track attempts
                if targetData[9]==0:
                    targetData[2]=targetData[1]/targetData[7]
            # Put target data into priority queue in priority order
            if targetData[2]>=self.priorityQueue[len(self.priorityQueue)-1][2]:
                self.priorityQueue.append(targetData)
            else:
                for i in range(len(self.priorityQueue)):
                    if targetData[2]<self.priorityQueue[i][2]:
                        self.priorityQueue.insert(i,targetData)
                        break
            print('CAOC Added target to priority queue')
            
            
class TargetRequest():
    
    def __init__(self, timestamp):
        self.timestamp = timestamp
        