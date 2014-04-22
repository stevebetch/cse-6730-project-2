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
        self.inputQueue = None
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
            if (msg.sender == 'CAOC' or msg.sender == 'HMINT'):
                self.inputQueue.addMessage(msg)
            else:
                self.caocInQ.addMessage(msg)
            if msg.color == LPGVTData.WHITE:
                if (msg.sender == 'CAOC' or msg.sender == 'HMINT'):
                    self.gvtData.counts[self.inputQueue.getLPID()] += 1
                else:
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
                print 'incrementing count of WHITE messages sent to drone %d' % (droneid)
                self.gvtData.counts[self.droneInQs.getLPID(droneid)] += 1
            else:
                print 'updating tRed value for drone %d' % (droneid)
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
        
        try:
            print 'Forwarding GVT control message to next LP'
            self.nextLPInTokenRingInQ.addMessage(msg)
        except:
            print 'Forwarding GVT control message to drone %d' % (self.nextDroneID)
            self.nextLPInTokenRingInQ.addMessage(self.nextDroneID, msg)
        
    def getNextLPInTokenRing(self, lpids):
        print self.LPID
        if (not (self.caocInQ is None) and self.caocInQ.getLPID() == self.LPID + 1):
            print 'next LP is CAOC'
            self.nextLPInTokenRingInQ = self.caocInQ
        elif (not (self.imintInQ is None) and self.imintInQ.getLPID() == self.LPID + 1):
            print 'next LP is IMINT'
            self.nextLPInTokenRingInQ = self.imintInQ
        else:
            # Drone or Controller
            self.nextLPInTokenRingInQ = self.droneInQs
            self.nextDroneID = self.droneInQs.getDroneIDForLPID(self.LPID + 1)            
            if self.nextDroneID is None:
                # This is last LP in token ring, will return token back to controller
                print 'this is last LP in token ring'
                self.nextLPInTokenRingInQ = self.controllerInQ
            else:
                print 'next LP is a drone'                
    
    def onGVTThreadFinished(self, lpids, msg):
        self.gvtData.initCounts(lpids)
        self.forwardGVTControlMessage(msg)
        print 'LP %d: GVT thread (cut C2) callback executed' % (self.LPID)
    
    def handleMessage(self, msg):
        print 'LP %d handleMessage' % (self.LPID)
        if msg.msgType == 1:
            if isinstance(msg.data, GVTControlMessageData):
                print 'LP %d received GVT control message' % (self.LPID)
                if self.gvtData.color == LPGVTData.WHITE:
                    print 'LP %d cut C1, changing color to Red' % (self.LPID)
                    # Cut C1, change color to red and add local counts of white msgs sent to control msg
                    self.gvtData.tRed = LPGVTData.INF
                    self.gvtData.color = LPGVTData.RED
                    msg.data.addLocalCounts(self.gvtData.counts, self.LPID)
                    self.forwardGVTControlMessage(msg)
                else:  # Cut C2
                    # Create new Thread to wait until num white msgs received by local process == num sent 
                    # to this process by all other processes
                    t = GVTWaitForThread(parent=self, controlMsg=msg)
                    print 'Starting GVT C2 cut thread in background'
                    t.start()
                    print 'Continuing after starting GVT C2 cut thread...'
            elif isinstance(msg.data, GVTValue):
                self.setGVT(msg.data.gvt)
        else:
            if msg.color == LPGVTData.WHITE:
                print 'LP %d recvd WHITE msg, rcvd count was %d' % (self.LPID, self.gvtData.counts[self.LPID])
                self.gvtData.counts[self.LPID] -= 1
                print 'LP %d recvd WHITE msg, rcvd count is now %d' % (self.LPID, self.gvtData.counts[self.LPID])
                self.gvtData.dump()
            if msg.timestamp < self.localTime:
                self.rollback(msg)
            else:
                self.saveState() #define getCurrentState() in subclass
                self.setLocalTime(msg.timestamp)
                self.inputMsgHistory.append(msg.clone())
                self.subclassHandleMessage(msg)
    
    def getNextMessage(self):
        msg = None
        q = None
        
        # if a drone, get local copy of input queue from DroneInputQueueContainer shared object 
        if self.inputQueue is None:
            q = self.droneInQs.getInputQueue(self.uid)
        else:
            q = self.inputQueue

        # get smallest timestamp message
        if q.hasMessages():
            msg = q.getNextMessage()
            
        # if a drone, save modified input queue back into DroneInputQueueContainer shared object    
        if self.inputQueue is None:
            self.droneInQs.setInputQueue(self.uid, q)
        
        return msg        
                
    def setLocalTime(self, time):
        self.localTime = time
        try:
            self.inputQueue.setLocalTime(time) 
        except:
            self.droneInQs.setLocalTime(self.uid, time)
        
    def saveAntiMessage(self, msg):
        antimsg = msg.getAntiMessage()
        self.outputQueue[msg.id] = antimsg
                
    def getLocalMinTimeForGVT(self):
        pass
    
    def setGVT(self, gvt):
        print 'LP %d setting GVT value to %d' % (self.LPID, gvt)
        self.gvt = gvt
        self.releaseResources(gvt)
        self.executeIO(gvt)
        
    def releaseResources(self, gvt):
        # delete items in state/output queues prior to GVT
        print 'LP %d releasing memory resources prior to GVT' % (self.LPID)
    
    def executeIO(self, gvt):
        # commit IO operations for times prior to GVT
        print 'LP %d committing I/O prior to GVT' % (self.LPID)
            