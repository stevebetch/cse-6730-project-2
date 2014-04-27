import sys
from Message import *
from SharedMemoryClient import *
from GVT import *
from GlobalControlProcess import *
from DroneInputQueueContainer import *
import threading

a = threading.Lock()
b=threading.Lock()
c=threading.Lock()
d=threading.Lock()
e = threading.Lock()

class LogicalProcess(SharedMemoryClient):
    # Implements Time Warp Local Control Mechanism

    nextLPID = 0
    CAOC_ID = 'CAOC'
    HMINT_ID = 'HMINT'
    IMINT_ID = 'IMINT'
    STUBLP_ID = 'STUBLP'
    
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
    def reset(self):
        LogicalProcess.nextLPID = 0
        self.stateQueue = []
        self.inputQueue = None
        self.outputQueue = {}
        self.inputMsgHistory = []
        self.localTime = 0
        self.gvtData.reset()
        del self.gvtData
        self.gvtData = []
        self.nextLPInTokenRingInQ = None
    
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
        
        #msg.printData(1)
        msg.color = self.gvtData.color            
        if(debug==1):
            if (msg.isAntiMessage()):
                print 'sending anti-message with timestamp %s' % (msg.timestamp)
            else:
                print 'sending message with timestamp %s' % (msg.timestamp)
            
        if (msg.recipient == LogicalProcess.HMINT_ID):
            e.acquire()
            self.hmintInQ.addMessage(msg)
            if msg.color == LPGVTData.WHITE:                
                self.gvtData.counts[self.hmintInQ.getLPID()] += 1
            else:
                self.gvtData.tRed = min(self.gvtData.tRed, msg.timestamp)
            e.release()
        elif (msg.recipient == LogicalProcess.STUBLP_ID):
            self.stublpInQ.addMessage(msg)
            if msg.color == LPGVTData.WHITE:                
                self.gvtData.counts[self.stublpInQ.getLPID()] += 1
            else:
                self.gvtData.tRed = min(self.gvtData.tRed, msg.timestamp)
        elif (msg.recipient == LogicalProcess.CAOC_ID):
            a.acquire()
            self.caocInQ.addMessage(msg)
            if msg.color == LPGVTData.WHITE:                
                self.gvtData.counts[self.caocInQ.getLPID()] += 1
            else:
                self.gvtData.tRed = min(self.gvtData.tRed, msg.timestamp)
            a.release()
        elif (msg.recipient == LogicalProcess.IMINT_ID):
            b.acquire()
            self.imintInQ.addMessage(msg)
            if msg.color == LPGVTData.WHITE:
                self.gvtData.counts[self.imintInQ.getLPID()] += 1
            else:
                self.gvtData.tRed = min(self.gvtData.tRed, msg.timestamp)
            b.release()
        elif (msg.recipient == GlobalControlProcess.CONTROLLER_ID):
            c.acquire()
            self.controllerInQ.addMessage(msg)
            c.release()
            # Controller not part of Logical Process GVT token ring
        else:
            # Drone
            d.acquire()
            droneid = msg.recipient
            
#            print "Drone ID for message:", droneid
            self.droneInQs.addMessage(droneid, msg) # assumes recipient set to drone's ID in msg
            if msg.color == LPGVTData.WHITE:
                if(debug==1):
                    print 'incrementing count of WHITE messages sent to drone %d' % (droneid)
                self.gvtData.counts[self.droneInQs.getLPID(droneid)] += 1
            else:
                if(debug==1):
                    print 'updating tRed value for drone %d' % (droneid)
                self.gvtData.tRed = min(self.gvtData.tRed, msg.timestamp)
            d.release()
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
                if(debug==1):
                    print 'add histMsg with timestamp %d to reprocess list' % histMsg.timestamp
                reprocessList.append(histMsg)

        # if a drone, get local copy of input queue from DroneInputQueueContainer shared object 
        if self.inputQueue is None:
            q = self.droneInQs.getInputQueue(self.uid)
        else:
            q = self.inputQueue 
        q.extend(reprocessList)
        if self.inputQueue is None:
            self.droneInQs.setInputQueue(self.uid, q)        
        
        # process straggler if not an anti-message
        if (not msg.isAntiMessage()):
            self.handleMessage(msg)  
            
    def forwardGVTControlMessage(self, msg):
        self.calculateLocalTMin()
        msg.data.tMin = min(msg.data.tMin, self.gvtData.tMin)
        msg.data.tRed = min(msg.data.tRed, self.gvtData.tRed)
        # send to next LP in ring
        if self.nextLPInTokenRingInQ is None:
            self.getNextLPInTokenRing(msg.data.LPIDs)
        
        try:
            if(debug==1):
                print 'Forwarding GVT control message to next LP'
            self.nextLPInTokenRingInQ.addMessage(msg)
        except:
            if(debug==1):
                print 'Forwarding GVT control message to drone %d' % (self.nextDroneID)
            self.nextLPInTokenRingInQ.addMessage(self.nextDroneID, msg)
            
    def forwardGVTValueMessage(self, msg):
        if self.nextLPInTokenRingInQ is None:
            self.getNextLPInTokenRing(msg.data.LPIDs)
        
        try:           
            self.nextLPInTokenRingInQ.addMessage(msg)
            if(debug==1):
                print 'Forwarding GVT value message to next LP'
        except:
            if(debug==1):
                print 'Forwarding GVT value message to drone %d' % (self.nextDroneID)
            self.nextLPInTokenRingInQ.addMessage(self.nextDroneID, msg)        
        
    def getNextLPInTokenRing(self, lpids):
        if(debug==1):
            print self.LPID
        if (not (self.hmintInQ is None) and self.hmintInQ.getLPID() == self.LPID + 1):
            if(debug==1):
                print 'next LP is HMINT'
            self.nextLPInTokenRingInQ = self.hmintInQ        
        elif (not (self.caocInQ is None) and self.caocInQ.getLPID() == self.LPID + 1):
            if(debug==1):
                print 'next LP is CAOC'
            self.nextLPInTokenRingInQ = self.caocInQ
        elif (not (self.imintInQ is None) and self.imintInQ.getLPID() == self.LPID + 1):
            if(debug==1):
                print 'next LP is IMINT'
            self.nextLPInTokenRingInQ = self.imintInQ
        else:
            # Drone or Controller
            self.nextLPInTokenRingInQ = self.droneInQs
            self.nextDroneID = self.droneInQs.getDroneIDForLPID(self.LPID + 1)            
            if self.nextDroneID is None:
                # This is last LP in token ring, will return token back to controller
                if(debug==1):
                    print 'this is last LP in token ring'
                self.nextLPInTokenRingInQ = self.controllerInQ
            else:
                if(debug==1):
                    print 'next LP is a drone'
                
    def calculateLocalTMin(self):
        # if a drone, get local copy of input queue from DroneInputQueueContainer shared object 
        if self.inputQueue is None:
            q = self.droneInQs.getInputQueue(self.uid)
        else:
            q = self.inputQueue        
        self.gvtData.tMin = q.calculateLocalTMin()        
    
    def onGVTThreadFinished(self, lpids, msg):
        self.gvtData.initCounts(lpids)
        if not(self.gvtData.tMin is None):
            msg.data.tMin = min(msg.data.tMin, self.gvtData.tMin)
        self.forwardGVTControlMessage(msg)
        if(debug==1):
            print 'LP %d: GVT thread (cut C2) callback executed' % (self.LPID)
    
    def handleMessage(self, msg):
        if(debug==1):
            print ''
            print 'LP %d handleMessage' % (self.LPID)
            print 'Current message:'
            msg.printData(0)
            print ''
            print 'Messages remaining in queue:'
        
        if self.inputQueue is None:
            q = self.droneInQs.getInputQueue(self.uid)
        else:
            q = self.inputQueue
        q.dump()
        if(debug==1):
            print ''

        if msg.msgType == 1:
            if isinstance(msg.data, GVTControlMessageData):
                if(debug==1):
                    print 'LP %d received GVT control message' % (self.LPID)
                if self.gvtData.color == LPGVTData.WHITE:
                    if(debug==1):
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
                    if(debug==1):
                        print 'Starting GVT C2 cut thread in background'
                    t.start()
                    if(debug==1):
                        print 'Continuing after starting GVT C2 cut thread...'
            elif isinstance(msg.data, GVTValue):
                self.setGVT(msg.data.gvt)
                self.forwardGVTValueMessage(msg)
        else:
            if msg.isAnti and not(self.matchingMessageAlreadyProcessed(msg)):
                # return antimessage to queue
                if self.inputQueue is None:
                    q = self.droneInQs.getInputQueue(self.uid)
                else:
                    q = self.inputQueue                        
                q.justPut(msg)
                if self.inputQueue is None:
                    self.droneInQs.setInputQueue(self.uid, q)
            elif msg.isAnti:
                if msg.timestamp <= self.localTime:
                    self.rollback(msg)
                elif msg.timestamp < self.localTime:
                    self.rollback(msg)
            else:
                if msg.timestamp < self.localTime:
                    self.rollback(msg)                
                else:
                    if msg.color == LPGVTData.WHITE:
                        if(debug==1):
                            print 'LP %d recvd WHITE msg, rcvd count was %d' % (self.LPID, self.gvtData.counts[self.LPID])
                        self.gvtData.counts[self.LPID] -= 1
                        if(debug==1):
                            print 'LP %d recvd WHITE msg, rcvd count is now %d' % (self.LPID, self.gvtData.counts[self.LPID])
                        if self.inputQueue is None:
                            if(debug==1):
                                print 'Number of WHITE msgs left in queue: %d' % (self.droneInQs.numWhiteMessages(self.uid))
                        else:
                            if(debug==1):
                                print 'Number of WHITE msgs left in queue: %d' % (self.inputQueue.numWhiteMessages())
                        self.gvtData.dump()                
                    self.saveState() #define getCurrentState() in subclass
                    if(debug==1):
                        print 'lp %d setting local time to %d' % (self.LPID, msg.timestamp)
                    self.setLocalTime(msg.timestamp)
                    self.inputMsgHistory.append(msg.clone())
                    self.subclassHandleMessage(msg)
                    sys.stdout.flush()
    
    def getNextMessage(self):
        a.acquire()
        b.acquire()
        c.acquire()
        d.acquire()
        e.acquire()
        
        msg = None
        q = None
        
        # if a drone, get local copy of input queue from DroneInputQueueContainer shared object 
        if self.inputQueue is None:
            q = self.droneInQs.getInputQueue(self.uid)
        else:
            q = self.inputQueue

        # get smallest timestamp message
        if q.hasMessages():
            if(debug==1):
                print 'LP %d queue has messages' % (self.LPID)
                sys.stdout.flush()
            msg = q.getNextMessage()
            
        # if a drone, save modified input queue back into DroneInputQueueContainer shared object    
        if self.inputQueue is None:
            self.droneInQs.setInputQueue(self.uid, q)
        
        a.release()
        b.release()
        c.release()
        d.release()
        e.release()
        return msg 
    
    def matchingMessageAlreadyProcessed(self, msg):
        for histMsg in self.inputMsgHistory:
            if histMsg.id == msg.id:
                return True
        return False
                
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
        return self.gvtData.tMin
    
    def setGVT(self, gvt):
        if(debug==1):
            print 'LP %d setting GVT value to %d' % (self.LPID, gvt)
        self.gvt = gvt
        self.releaseResources(gvt)
        self.executeIO(gvt)
        
    def releaseResources(self, gvt):
        # delete items in state/history/output queues prior to GVT
        if(debug==1):
            print 'LP %d releasing memory resources prior to GVT' % (self.LPID)
        # outputQueue
            print 'outputQueue length before reclaim: %d' % (len(self.outputQueue))
        temp = {}
        for msgID, antimessage in self.outputQueue.items():
            if antimessage.timestamp >= gvt:
                temp[msgID] = antimessage
        self.outputQueue = temp
        if(debug==1):
            print 'outputQueue length after reclaim: %d' % (len(self.outputQueue))
        # stateQueue
        temp = []
        if(debug==1):
            print 'stateQueue length before reclaim: %d' % (len(self.stateQueue))
        for i in self.stateQueue:
            if i.localTime >= gvt:
                temp.append(i)
        self.stateQueue = temp
        if(debug==1):
            print 'stateQueue length after reclaim: %d' % (len(self.stateQueue))
        # message history
        temp = []
        if(debug==1):
            print 'inputMsgHistory length before reclaim: %d' % (len(self.inputMsgHistory))
        for msg in self.inputMsgHistory:
            if msg.timestamp >= gvt:
                temp.append(msg)
        self.inputMsgHistory = temp
        if(debug==1):
            print 'inputMsgHistory length after reclaim: %d' % (len(self.inputMsgHistory))
    
    def executeIO(self, gvt):
        # commit IO operations for times prior to GVT
        if(debug==1):
            print 'LP %d committing I/O prior to GVT' % (self.LPID)
            