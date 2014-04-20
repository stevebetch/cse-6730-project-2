import sys
from Message import *
from SharedMemoryClient import *
from GVT import *
from DroneInputQueueContainer import *
from threading import Thread


class LogicalProcess(SharedMemoryClient):
    # Implements Time Warp Local Control Mechanism
    
    nextLPID = 0
    
    # Get next Logical Process ID Function
    # Description: Provide unique ids for new logical processes
    # Input: None
    # Output: LP ID integer
    def getNextLPID(self):
        LPID = LogicalProcess.nextLPID
        LogicalProcess.nextLPID += 1
        return LPID    
    
    # instance variable list
    #inputQueue - FIFO queue for incoming messages
    #stateQueue - dictionary of timestamp (keys) to state object (values)
    #outputQueue - dictionary of message id (keys) to antimessage (values)
    #localTime - current time logical process is at
    #gvt - last gvt value received from controller
    
    
    def __init__(self): 
        self.LPID = self.getNextLPID()     
        self.stateQueue = []
        self.inputQueue=DroneInputQueueContainer()
        self.outputQueue = {}
        self.inputMsgHistory = []
        self.localTime = 0
        self.gvtData = LPGVTData()
        self.nextLPInTokenRingInQ = None
        
    def initGVTCounts(self, lpids):
        self.gvtData.initCounts(lpids)
        
    def sendMessage(self, msg):
        
        msg.color = self.gvtData.color            
            
        if (msg.isAntiMessage()):
            print 'sending anti-message with timestamp %s' % (msg.timestamp)
        else:
            print 'sending message with timestamp %s' % (msg.timestamp)
            
        if (msg.recipient == 'CAOC'):
            self.caocInQ.addMessage(msg)
            if msg.color == LPGVTData.WHITE:
                self.gvtData.counts[self.caocInQ.getLPID()] += 1
            else:
                self.gvtData.tRed = min(self.gvtData.tRed, msg.timestamp)
        elif (msg.recipient == 'IMINT'):
            self.imintInQ.addMessage(msg)
            if msg.color == LPGVTData.WHITE:
                self.gvtData.counts[self.imintInQ.getLPID()] += 1
            else:
                self.gvtData.tRed = min(self.gvtData.tRed, msg.timestamp)                
        elif (msg.recipient == 'Controller'):
            self.controllerInQ.addMessage(msg)
            # Controller not part of Logical Process GVT token ring
        else:
            # Drone
            droneid = msg.recipient
            self.droneInQs.addMessage(droneid, msg) # assumes recipient set to drone's ID in msg
            if msg.color == LPGVTData.WHITE:
                self.gvtData.counts[self.droneInQs.getLPID(droneid)] += 1
            else:
                self.gvtData.tRed = min(self.gvtData.tRed, msg.timestamp)

        self.saveAntiMessage(msg)
    
    def rollback(self, msg):
        
        print 'ROLLBACK!!'
        # restore state to that at time of straggler message
        self.restoreState(msg.timestamp) # define restoreState(timestamp) in subclass
        
        # send anti-messages for all messages sent after straggler message
        for uid in self.outputQueue:
            if self.outputQueue[uid].timestamp > msg.timestamp:
                self.sendMessage(self.outputQueue[uid])
                
        # set local time to time of straggler, prevents recursive calling of rollback message
        self.localTime = msg.timestamp
        
        # append messages processed after this time to input queue for reprocessing
        reprocessList = []
        for histMsg in self.inputMsgHistory:
            if histMsg.timestamp > msg.timestamp:
                reprocessList.append(histMsg)
        reprocessList.sort(key=lambda x: x.timestamp, reverse=True)
        self.inputQueue.extend(reprocessList)
        
        # process straggler if not an anti-message
        if (not msg.isAntiMessage()):
            self.handleMessage(msg)  
            
    def forwardGVTControlMessage(self, msg):
        msg.data.tMin = min(msg.data.tMin, self.gvtData.tMin)
        msg.data.tRed = min(msg.data.tRed, self.gvtData.tRed)
        # send to next LP in ring
        if self.nextLPInTokenRingInQ is None:
            self.getNextLPInTokenRing(msg.data.LPIDs)
        self.nextLPInTokenRingInQ.addMessage(msg)
        
    def getNextLPInTokenRing(self, lpids):
        print self.LPID
        if (not (self.caocInQ is None) and self.caocInQ.getLPID() == self.LPID + 1):
            print 'next LP is CAOC'
            self.nextLPInTokenRingInQ = self.caocInQ
        elif (not (self.imintInQ is None) and self.imintInQ.getLPID() == self.LPID + 1):
            print 'next LP is IMINT'
            self.nextLPInTokenRingInQ = self.imintInQ
        else:
            # Drone
            self.nextLPInTokenRingInQ = self.droneInQs.getNextLPInputQueue(self.LPID)
            # This is last LP in token ring, will return token back to controller
            if self.nextLPInTokenRingInQ is None:
                print 'this is last LP in token ring'
                self.nextLPInTokenRingInQ = self.controllerInQ
            else:
                print 'next LP is a drone'
    
    def onGVTThreadFinished(self, lpids, msg):
        self.gvtData.initCounts(lpids)
        self.forwardGVTControlMessage(msg)
        print 'GVT thread callback executed'
    
    def handleMessage(self, msg):

        if msg.msgType == 1 and isinstance(msg.data, GVTControlMessageData):
            # handle GVT control message
            if self.gvtData.color == LPGVTData.WHITE:
                # Cut C1, change color to red and add local counts of white msgs sent to control msg
                self.gvtData.tRed = LPGVTData.INF
                self.gvtData.color = LPGVTData.RED
                msg.data.addLocalCounts(self.gvtData.counts)
                self.forwardGVTControlMessage(msg)
            else:  # Cut C2
                # Create new Thread to wait until num white msgs received by local process == num sent 
                # to this process by all other processes
                t = GVTWaitForThread(parent=self, controlMsg=msg, localCounts=self.gvtData.counts)
                print 'Starting GVT C2 cut thread in background'
                t.start()
                print 'Continuing after starting GVT C2 cut thread...'            
        else:
            if msg.color == LPGVTData.WHITE:
                self.gvtData.counts[self.LPID] -= 1
            if msg.timestamp < self.localTime:
                self.rollback(msg)
            else:
                self.saveState() #define getCurrentState() in subclass
                self.setLocalTime(msg.timestamp)
                self.inputMsgHistory.append(msg.clone())
                self.subclassHandleMessage(msg)
    
    def getNextMessage(self):
        msg = None       
        if self.inputQueue.hasMessages():
            # peek at first message
            firstMsg = self.inputQueue.getNextMessage()
            if firstMsg is None:
                self.inputQueue.remove(firstMsg)
            elif (not firstMsg.isAntiMessage()):
                #print 'Found First Message (not an AntiMessage)'
                return firstMsg
            elif (firstMsg.timestamp <= self.localTime):
                print 'Found First Message (AntiMessage w/ ts <= localTime)'
                return firstMsg
            else:
                #print 'Found First Message is an AntiMessage, returning to queue'
                self.inputQueue.justPut(firstMsg)
                # loop until non-antiMessage is found
                while True:
                    currMsg = self.inputQueue.getNextMessage()
                    if currMsg == firstMsg:
                        self.inputQueue.justPut(currMsg)
                        #print 'All messages in queue are AntiMessages'
                        break
                    if (currMsg.isAntiMessage()):
                        if (firstMsg.timestamp <= self.localTime):
                            print 'Found Message (AntiMessage w/ ts <= localTime)'
                            return currMsg
                        else:
                            # put it back and get another one
                            #print 'Found AntiMessage, returning to queue'
                            self.inputQueue.justPut(currMsg)                        
                    else:
                        #print 'Found Message'
                        msg = currMsg
                        break
        return msg        
                
    def setLocalTime(self, time):
        self.localTime = time
        self.inputQueue.setLocalTime(time)        
        
    def saveAntiMessage(self, msg):
        antimsg = msg.getAntiMessage()
        self.outputQueue[msg.id] = antimsg
                
    def getLocalMinTimeForGVT(self):
        pass
    
    def setGVT(self, gvt):
        self.gvt = gvt
        releaseResources(gvt)
        executeIO(gvt)
        
    def releaseResources(self):
        # delete items in state/output queues prior to GVT
        pass
    
    def executeIO(gvt):
        # commit IO operations for times prior to GVT
        pass
            